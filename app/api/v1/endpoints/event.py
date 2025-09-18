from fastapi import APIRouter, Depends, Path
from typing import Annotated
from fastapi_jwt_auth import AuthJWT

from model.response_models import ApiResponse
from model.schedule.event.schemas import EventDetailResponse, EventEditRequest, EventResponse
from app.services.user_service import UserService # To get user from subject
from app.services.event_service import EventService, CustomException

router = APIRouter()

@router.get("/{event_id}", response_model=ApiResponse[EventDetailResponse])
def get_event_detail(
    event_id: Annotated[int, Path(ge=1)],
    event_service: Annotated[EventService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    event = event_service.get_event_detail(event_id, username)
    return ApiResponse(message="이벤트를 조회하였습니다.", data=event)

@router.put("/{event_id}", response_model=ApiResponse[None])
def edit_event(
    event_id: Annotated[int, Path(ge=1, alias="eventId")],
    request: EventEditRequest,
    event_service: Annotated[EventService, Depends()],
    Authorize: AuthJWT = Depends()
):
    username = Authorize.get_jwt_subject()
    event_service.edit_event(event_id, request, username)
    return ApiResponse(message="이벤트를 수정하였습니다.", data=None)

@router.delete("/{event_id}", response_model=ApiResponse[None])
def delete_event(
    event_id: Annotated[int, Path(ge=1, alias="eventId")],
    event_service: Annotated[EventService, Depends()],
    Authorize: AuthJWT = Depends()
):
    username = Authorize.get_jwt_subject()
    event_service.delete_event(event_id, username)
    return ApiResponse(message="이벤트를 삭제하였습니다.", data=None)
