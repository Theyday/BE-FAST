from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated, List, Union
from datetime import date

from model.ai.schemas import AIEventResponse, AITaskResponse
from model.response_models import ApiResponse
from model.schedule.schemas import CalendarItemDto, ScheduleType
from app.services.schedule_service import ScheduleService
from core.jwt_security import get_current_user_id

router = APIRouter()

@router.get("/range", response_model=ApiResponse[List[CalendarItemDto]])
async def get_calendar_items_by_range(
    start_date: Annotated[date, Query(alias="startDate")],
    end_date: Annotated[date, Query(alias="endDate")],
    schedule_service: Annotated[ScheduleService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    items = await schedule_service.get_calendar_items_by_range(start_date, end_date, current_user_id)
    return ApiResponse(message="기간 내 캘린더 데이터를 조회하였습니다.", data=items)

@router.post("/{schedule_id}/type", response_model=ApiResponse[Union[AIEventResponse, AITaskResponse]])
async def change_schedule_type(
    schedule_id: Annotated[int, Path(ge=1)],
    current_type: Annotated[ScheduleType, Query(alias="currentType")],
    schedule_service: Annotated[ScheduleService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    result = await schedule_service.change_schedule_type(schedule_id, current_type, current_user_id)
    return ApiResponse(message="일정 타입을 변경하였습니다.", data=result)
