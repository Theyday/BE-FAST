from fastapi import APIRouter, Depends, Path
from typing import Annotated
from core.jwt_security import get_current_user_id

from model.response_models import ApiResponse
from model.schedule.event.schemas import EventDetailResponse, EventEditRequest
from app.services.event_service import EventService

router = APIRouter()

@router.get("/{event_id}", response_model=ApiResponse[EventDetailResponse])
async def get_event_detail(
    event_id: Annotated[int, Path(ge=1)],
    event_service: Annotated[EventService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    event = await event_service.get_event_detail(event_id, current_user_id)
    return ApiResponse(message="이벤트를 조회하였습니다.", data=event)

@router.put("/{event_id}", response_model=ApiResponse[None])
async def edit_event(
    event_id: Annotated[int, Path(ge=1)],
    request: EventEditRequest,
    event_service: Annotated[EventService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await event_service.edit_event(event_id, request, current_user_id)
    return ApiResponse(message="이벤트를 수정하였습니다.", data=None)

@router.delete("/{event_id}", response_model=ApiResponse[None])
async def delete_event(
    event_id: Annotated[int, Path(ge=1)],
    event_service: Annotated[EventService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await event_service.delete_event(event_id, current_user_id)
    return ApiResponse(message="이벤트를 삭제하였습니다.", data=None)
