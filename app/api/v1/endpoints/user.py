from fastapi import APIRouter, Depends
from typing import Annotated
from model.response_models import ApiResponse
from model.user.schemas import SignUpRequest, TokenResponse, DeviceTokenRequest
from app.services.user_service import UserService
from core.jwt_security import get_current_user_id

router = APIRouter()

@router.get("/send-code", response_model=ApiResponse[bool])
async def send_code(value: str, user_service: Annotated[UserService, Depends()]):
    is_user = await user_service.send_code(value)

    return ApiResponse(message="인증번호 전송 완료", data=is_user)

@router.get("/verify-code", response_model=ApiResponse[bool])
async def verify_code(value: str, code: str, user_service: Annotated[UserService, Depends()]):
    is_valid = await user_service.verify_code(value, code)
    return ApiResponse(message="인증번호 검증 완료", data=is_valid)

@router.get("/sign-in", response_model=ApiResponse[TokenResponse])
async def sign_in(value: str, code: str, user_service: Annotated[UserService, Depends()]):
    token_response = await user_service.sign_in(value, code)
    return ApiResponse(message="로그인에 성공하였습니다.", data=token_response)

@router.post("/sign-up", response_model=ApiResponse[TokenResponse])
async def sign_up(request: SignUpRequest, user_service: Annotated[UserService, Depends()]):
    token_response = await user_service.sign_up(request)
    return ApiResponse(message="회원가입에 성공하였습니다.", data=token_response)

@router.get("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(user_service: Annotated[UserService, Depends()], current_user_id: int = Depends(get_current_user_id)):
    token_response = await user_service.refresh(current_user_id)
    return ApiResponse(message="토큰 갱신에 성공하였습니다.", data=token_response)

@router.post("/device-token", response_model=ApiResponse[None])
async def register_device_token(request: DeviceTokenRequest, user_service: Annotated[UserService, Depends()], current_user_id: int = Depends(get_current_user_id)):
    print(current_user_id)
    user = await user_service._load_user_by_id(current_user_id)
    user_id = user.id if user else None
    await user_service.register_device_token(request, user_id)
    return ApiResponse(message="디바이스 토큰을 등록하였습니다.", data=None)

@router.delete("/device-token", response_model=ApiResponse[None])
async def delete_device_token(token: str, user_service: Annotated[UserService, Depends()]):
    await user_service.delete_device_token(token)
    return ApiResponse(message="디바이스 토큰을 삭제하였습니다.", data=None)
