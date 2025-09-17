from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated, List, Union
from datetime import date
from fastapi_jwt_auth import AuthJWT

from model.response_models import ApiResponse
from model.schedule.schemas import CalendarItemDto, ScheduleType
from app.services.user_service import UserService # To get user from subject
from app.services.schedule_service import ScheduleService, CustomException

router = APIRouter()

@router.get("/range", response_model=ApiResponse[List[CalendarItemDto]])
def get_calendar_items_by_range(
    start_date: Annotated[date, Query(alias="startDate")],
    end_date: Annotated[date, Query(alias="endDate")],
    schedule_service: Annotated[ScheduleService, Depends()],
    Authorize: AuthJWT = Depends(),

):
    username = Authorize.get_jwt_subject()
    print(username)
    user_id_temp = 1
    items = schedule_service.get_calendar_items_by_range(start_date, end_date, user_id_temp)
    return ApiResponse(message="기간 내 캘린더 데이터를 조회하였습니다.", data=items)

@router.post("/{schedule_id}/type", response_model=ApiResponse[Union[dict, None]])
def change_schedule_type(
    schedule_id: Annotated[int, Path(ge=1, alias="scheduleId")],
    current_type: Annotated[ScheduleType, Query(alias="currentType")],
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    schedule_service: Annotated[ScheduleService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    result = schedule_service.change_schedule_type(schedule_id, current_type, user_id)
    return ApiResponse(message="일정 타입을 변경하였습니다.", data=result)
