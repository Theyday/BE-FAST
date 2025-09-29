import random
import redis
from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession # AsyncSession 임포트

from core.config import settings
from core.jwt_security import create_access_token, create_refresh_token # JWT 헬퍼 함수 임포트
from model.database import get_async_session # 비동기 세션 임포트
from model.user.crud import user_crud, user_device_token_crud
from model.category.crud import category_crud
from model.schedule.routine.crud import routine_crud
from model.user import models as user_models
from model.user import schemas as user_schemas
from model.user.deviceToken import models as user_device_token_models
from app.services.sms_service import SmsService
from app.services.mail_service import MailService

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class UserService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_async_session), # AsyncSession 사용
        mail_service: MailService = Depends(),
        sms_service: SmsService = Depends(),
        redis_client: redis.Redis = Depends(lambda: redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)),
    ):
        self.db = db
        self.mail_service = mail_service
        self.sms_service = sms_service
        self.redis_client = redis_client

    async def _create_verification_code(self) -> str:
        return str(random.randint(100000, 999999))

    async def _load_user_by_id(self, user_id: int) -> user_models.User:
        user = await user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def send_code(self, value: str) -> bool:
        if value == "01062013110":  # Hardcoded test number
            self.redis_client.setex(
                f"verification:{value}",
                timedelta(minutes=settings.PHONE_VERIFICATION_EXPIRATION),
                "123456"
            )
            return True

        is_exist = False
        verification_code = await self._create_verification_code()
        
        if "@" in value:
            is_exist = await user_crud.exists_by_email(self.db, value)
            self.redis_client.setex(
                f"verification:{value}",
                timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRATION),
                verification_code
            )
            self.mail_service.send_simple_mail_message(value, verification_code, is_exist)
        else:
            is_exist = await user_crud.exists_by_phone(self.db, value)
            self.redis_client.setex(
                f"verification:{value}",
                timedelta(minutes=settings.PHONE_VERIFICATION_EXPIRATION),
                verification_code
            )
            try:
                self.sms_service.send_sms(value, verification_code)
            except Exception as e:
                raise CustomException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS send failed") from e
        return is_exist

    async def verify_code(self, value: str, code: str) -> bool:
        stored_code = self.redis_client.get(f"verification:{value}")
        if stored_code is None or stored_code.decode("utf-8") != code:
            return False
        
        self.redis_client.delete(f"verification:{value}")
        return True

    async def sign_in(self, value: str, code: str) -> user_schemas.TokenResponse:
        if not await self.verify_code(value, code):
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
        
        user = await user_crud.get_user_by_email_or_phone(self.db, value)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in login")

        identity = user.id
        access_token = create_access_token(data={"sub": str(identity)})
        refresh_token = create_refresh_token(data={"sub": str(identity)})

        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token, userId=identity)

    async def sign_up(self, request: user_schemas.SignUpRequest) -> user_schemas.TokenResponse:
        if len(request.name) > 10:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name length")
        
        user = await user_crud.create_user(self.db, request)

        await category_crud.create_default(self.db, user)
        await routine_crud.create_default_routines_for_user(self.db, user)

        identity = user.id 
        access_token = create_access_token(data={"sub": str(identity)})
        refresh_token = create_refresh_token(data={"sub": str(identity)})
        
        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token, userId=identity)

    async def refresh(self, current_user_id: int) -> user_schemas.TokenResponse:
        
        access_token = create_access_token(data={"sub": str(current_user_id)})
        refresh_token = create_refresh_token(data={"sub": str(current_user_id)})
        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token)

    async def register_device_token(self, request: user_schemas.DeviceTokenRequest, user_id: Optional[int]) -> None:
        device_token = await user_device_token_crud.find_by_token(self.db, request.token)

        user = None
        if user_id:
            user = await user_crud.get_user_by_id(self.db, user_id)
            if not user:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if device_token:
            device_token.user = user
            await user_device_token_crud.save_device_token(self.db, device_token)
        else:
            new_device_token = user_device_token_models.UserDeviceToken(
                user_id=user_id if user_id else None,
                token=request.token
            )
            await user_device_token_crud.save_device_token(self.db, new_device_token)

    async def delete_device_token(self, token: str, user_id: int) -> None:
        # user_id를 사용하여 특정 사용자의 디바이스 토큰만 삭제하도록 변경
        await user_device_token_crud.delete_by_token(self.db, token, user_id)
