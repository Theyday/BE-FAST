import random
import redis
from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from core.config import settings
from model.database import get_db
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
        db: Session = Depends(get_db),
        mail_service: MailService = Depends(),
        sms_service: SmsService = Depends(),
        redis_client: redis.Redis = Depends(lambda: redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)),
        Authorize: AuthJWT = Depends()
    ):
        self.db = db
        self.mail_service = mail_service
        self.sms_service = sms_service
        self.redis_client = redis_client
        self.Authorize = Authorize

    def _create_verification_code(self) -> str:
        return str(random.randint(100000, 999999))

    def _load_user_by_username(self, username: str) -> user_models.User:
        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def send_code(self, value: str) -> bool:
        if value == "01062013110":  # Hardcoded test number
            self.redis_client.setex(
                f"verification:{value}",
                timedelta(minutes=settings.PHONE_VERIFICATION_EXPIRATION),
                "123456"
            )
            return True

        is_exist = False
        verification_code = self._create_verification_code()
        
        if "@" in value:
            is_exist = user_crud.exists_by_email(self.db, value)
            self.redis_client.setex(
                f"verification:{value}",
                timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRATION),
                verification_code
            )
            self.mail_service.send_simple_mail_message(value, verification_code, is_exist)
        else:
            is_exist = user_crud.exists_by_phone(self.db, value)
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

    def verify_code(self, value: str, code: str) -> bool:
        stored_code = self.redis_client.get(f"verification:{value}")
        if stored_code is None or stored_code.decode("utf-8") != code:
            return False
        
        self.redis_client.delete(f"verification:{value}")
        return True

    def sign_in(self, value: str, code: str) -> user_schemas.TokenResponse:
        if not self.verify_code(value, code):
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
        
        user = user_crud.get_user_by_email_or_phone(self.db, value)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in login")

        # Generate JWT tokens
        identity = user.email if user.email else user.phone
        access_token = self.Authorize.create_access_token(subject=identity)
        refresh_token = self.Authorize.create_refresh_token(subject=identity)

        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token)

    def sign_up(self, request: user_schemas.SignUpRequest) -> user_schemas.TokenResponse:
        if len(request.name) > 10:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name length")
        
        user = user_crud.create_user(self.db, request)

        category_crud.create_default(self.db, user)
        routine_crud.create_default_routines_for_user(self.db, user)

        # Generate JWT tokens
        identity = user.email if user.email else user.phone
        access_token = self.Authorize.create_access_token(subject=identity)
        refresh_token = self.Authorize.create_refresh_token(subject=identity)
        
        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token)

    def refresh(self) -> user_schemas.TokenResponse:
        
        current_user = self.Authorize.get_jwt_subject()
        access_token = self.Authorize.create_access_token(subject=current_user)
        refresh_token = self.Authorize.create_refresh_token(subject=current_user)
        return user_schemas.TokenResponse(accessToken=access_token, refreshToken=refresh_token)

    def register_device_token(self, request: user_schemas.DeviceTokenRequest, user_id: Optional[int]) -> None:
        device_token = user_device_token_crud.find_by_token(self.db, request.token)

        user = None
        if user_id:
            user = user_crud.get_user_by_id(self.db, user_id)
            if not user:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if device_token:
            device_token.user = user
            user_device_token_crud.save_device_token(self.db, device_token)
        else:
            new_device_token = user_device_token_models.UserDeviceToken(
                user_id=user_id if user_id else None,
                token=request.token
            )
            user_device_token_crud.save_device_token(self.db, new_device_token)

    def delete_device_token(self, token: str) -> None:
        user_device_token_crud.delete_by_token(self.db, token)
