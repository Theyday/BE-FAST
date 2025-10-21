from fastapi import APIRouter, Depends, Path
from typing import Annotated
from core.jwt_security import get_current_user_id

from model.response_models import ApiResponse

router = APIRouter()
@router.get("/alerts", response_model=ApiResponse)
async def get_user_alert_settings(
    current_user_id: int = Depends(get_current_user_id)
):
    return ApiResponse(message="알림 설정을 조회하였습니다.", data=[])