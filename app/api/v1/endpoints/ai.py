from fastapi import APIRouter, Depends
from typing import Annotated, Union
from fastapi_jwt_auth import AuthJWT

from model.response_models import ApiResponse
from model.ai.schemas import CreateFromTextRequest, AIEventResponse, AITaskResponse
from app.services.ai_service import AiService

router = APIRouter()


@router.post("/create-from-text", response_model=ApiResponse[Union[AIEventResponse, AITaskResponse]])
def create_from_text(
    request: CreateFromTextRequest,
    ai_service: Annotated[AiService, Depends()],
    Authorize: AuthJWT = Depends(),
):
    """텍스트 기반으로 EVENT 또는 TASK 생성"""
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    result = ai_service.create_from_text(request, username)
    return ApiResponse(message="텍스트 기반 생성을 완료하였습니다.", data=result)


@router.post("/create-from-text/trial", response_model=ApiResponse[Union[AIEventResponse, AITaskResponse]])
def create_from_text_trial(
    request: CreateFromTextRequest,
    ai_service: Annotated[AiService, Depends()],
):
    """텍스트 기반으로 EVENT 또는 TASK 생성 (체험용)"""
    result = ai_service.create_from_text_trial(request)
    return ApiResponse(message="텍스트 기반 생성 체험", data=result)
