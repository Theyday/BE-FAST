from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi_jwt_auth import AuthJWT

from ....model.database import get_db
from ....model.response_models import ApiResponse
from ....model.user.schemas import SignUpRequest, TokenResponse, DeviceTokenRequest
from ....app.services.user_service import UserService, CustomException

router = APIRouter()

@router.get("/send-code", response_model=ApiResponse[bool])
def send_code(value: str, user_service: Annotated[UserService, Depends()]):
    is_user = user_service.send_code(value)
    return ApiResponse(message="인증번호 전송 완료", data=is_user)

@router.get("/verify-code", response_model=ApiResponse[bool])
def verify_code(value: str, code: str, user_service: Annotated[UserService, Depends()]):
    is_valid = user_service.verify_code(value, code)
    return ApiResponse(message="인증번호 검증 완료", data=is_valid)

@router.get("/sign-in", response_model=ApiResponse[TokenResponse])
def sign_in(value: str, code: str, user_service: Annotated[UserService, Depends()]):
    token_response = user_service.sign_in(value, code)
    return ApiResponse(message="로그인에 성공하였습니다.", data=token_response)

@router.post("/sign-up", response_model=ApiResponse[TokenResponse])
def sign_up(request: SignUpRequest, user_service: Annotated[UserService, Depends()]):
    token_response = user_service.sign_up(request)
    return ApiResponse(message="회원가입에 성공하였습니다.", data=token_response)

@router.get("/refresh", response_model=ApiResponse[TokenResponse])
def refresh(authorization: Annotated[str, Header()], user_service: Annotated[UserService, Depends()]):
    token_response = user_service.refresh(authorization)
    return ApiResponse(message="토큰 갱신에 성공하였습니다.", data=token_response)

@router.post("/device-token", response_model=ApiResponse[None])
def register_device_token(request: DeviceTokenRequest, user_service: Annotated[UserService, Depends()], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() # Verify access token validity
    current_user_identity = Authorize.get_jwt_subject()
    # Assuming current_user_identity is the email or phone, retrieve the user ID
    user = user_service._load_user_by_username(current_user_identity)
    user_id = user.id if user else None
    user_service.register_device_token(request, user_id)
    return ApiResponse(message="디바이스 토큰을 등록하였습니다.", data=None)

@router.delete("/device-token", response_model=ApiResponse[None])
def delete_device_token(token: str, user_service: Annotated[UserService, Depends()]):
    user_service.delete_device_token(token)
    return ApiResponse(message="디바이스 토큰을 삭제하였습니다.", data=None)
