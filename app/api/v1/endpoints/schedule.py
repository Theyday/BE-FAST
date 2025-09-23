from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated, List, Union
from datetime import date

from model.ai.schemas import AIEventResponse, AITaskResponse
from model.response_models import ApiResponse
from model.schedule.schemas import CalendarItemDto, ScheduleType, ScheduleDetailsRequest
from app.services.event_service import EventService
from app.services.schedule_service import ScheduleService
from app.services.task_service import TaskService
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

"""
POST /api/v1/schedules/details
Request Body: { "eventIds": [1, 5, 12], "taskIds": [8, 15] }
Response Body: { "events": [ ... ], "tasks": [ ... ] }
"""
@router.post("/details")
async def get_schedule_details(
    request: ScheduleDetailsRequest,
    # event_ids: Annotated[List[int], Query(alias="eventIds")],
    # task_ids: Annotated[List[int], Query(alias="taskIds")],
    event_service: Annotated[EventService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    events = []
    tasks = []
    if request.event_ids != []:
        for event_id in request.event_ids:
            event = await event_service.get_event_detail(event_id, current_user_id)
            events.append(event)

    if request.task_ids != []:
        for task_id in request.task_ids:
            task = await task_service.get_task_detail(task_id, current_user_id)
            tasks.append(task)

    details = {
        "events": events,
        "tasks": tasks
    }

    return ApiResponse(message="일정 상세 정보를 조회하였습니다.", data=details)