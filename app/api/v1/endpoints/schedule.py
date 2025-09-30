from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated, List, Union
from datetime import date

from app.services.task_service import TaskService
from app.services.routine_service import RoutineService
from model.ai.schemas import AIEventResponse, AITaskResponse
from model.response_models import ApiResponse
from model.schedule.event import schemas as event_schemas
from model.schedule.routine import schemas as routine_schemas
from model.category import schemas as category_schemas
from model.schedule.schemas import CalendarItemDto, ScheduleBatchRequest, ScheduleType, ScheduleDetailsRequest
from app.services.event_service import EventService
from app.services.schedule_service import ScheduleService
from app.services.category_service import CategoryService
from core.jwt_security import get_current_user_id
from model.schedule.task import schemas as task_schemas

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

@router.post("/batch")
async def post_schedule_batch(
    request: ScheduleBatchRequest,
    event_service: Annotated[EventService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    routine_service: Annotated[RoutineService, Depends()],
    category_service: Annotated[CategoryService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    """
    tableName	“events” | “tasks” | “routines” | “categories”	어떠한 모델에 대한 수정인지
    tempId	string	기존의 임시 ID
    serverId	string	새로 생성된 서버의 ID
    """
    mapping_list = [] # response로 반환할 매핑 리스트

    for operation in request.operations:
        if operation.table_name == "events":
            if operation.operation == "create":
                if operation.payload["categoryId"] in [item["tempId"] for item in mapping_list]:
                    operation.payload["categoryId"] = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.payload["categoryId"])
                event_create_request = event_schemas.EventCreateRequest.model_validate(operation.payload)
                real_event = await event_service.create_event(event_create_request, current_user_id)
                mapping_list.append({"tableName": "events", "tempId": operation.row_id, "serverId": real_event.id})
            elif operation.operation == "update":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "events"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "events")
                if operation.payload["categoryId"] in [item["tempId"] for item in mapping_list]:
                    operation.payload["categoryId"] = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.payload["categoryId"])
                event_edit_request = event_schemas.EventEditRequest.model_validate(operation.payload)
                await event_service.edit_event(int(operation.row_id), event_edit_request, current_user_id)
            elif operation.operation == "delete":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "events"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "events")
                    mapping_list = [item for item in mapping_list if not (item["tableName"] == "events" and item["serverId"] == operation.row_id)]
                await event_service.delete_event(int(operation.row_id), current_user_id)
        elif operation.table_name == "tasks":
            if operation.operation == "create":
                if "categoryId" in operation.payload and operation.payload["categoryId"] in [item["tempId"] for item in mapping_list]:
                    operation.payload["categoryId"] = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.payload["categoryId"])
                task_create_request = task_schemas.TaskCreateRequest.model_validate(operation.payload)
                real_task = await task_service.create_task(task_create_request, current_user_id)
                mapping_list.append({"tableName": "tasks", "tempId": operation.row_id, "serverId": real_task.id})
            elif operation.operation == "update":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "tasks"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "tasks")
                if "categoryId" in operation.payload and operation.payload["categoryId"] in [item["tempId"] for item in mapping_list]:
                    operation.payload["categoryId"] = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.payload["categoryId"])
                task_edit_request = task_schemas.TaskEditRequest.model_validate(operation.payload)             
                await task_service.edit_task(int(operation.row_id), task_edit_request, current_user_id)
            elif operation.operation == "delete":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "tasks"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "tasks")
                    mapping_list = [item for item in mapping_list if not (item["tableName"] == "tasks" and item["serverId"] == operation.row_id)]
                await task_service.delete_task(int(operation.row_id), current_user_id)
        elif operation.table_name == "routines":
            if operation.operation == "create":
                routine_create_request = routine_schemas.RoutineCreateRequest.model_validate(operation.payload)
                real_routine = await routine_service.create_routine(routine_create_request, current_user_id)
                mapping_list.append({"tableName": "routines", "tempId": operation.row_id, "serverId": real_routine.id})
            elif operation.operation == "update":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "routines"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "routines")
                routine_edit_request = routine_schemas.RoutineCreateRequest.model_validate(operation.payload)
                await routine_service.update_routine(int(operation.row_id), routine_edit_request, current_user_id)
            elif operation.operation == "delete":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "routines"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "routines")
                    mapping_list = [item for item in mapping_list if not (item["tableName"] == "routines" and item["serverId"] == operation.row_id)]
                await routine_service.delete_routine(int(operation.row_id), current_user_id)
        elif operation.table_name == "categories":
            if operation.operation == "create":
                category_create_request = category_schemas.CategoryCreate.model_validate(operation.payload)
                real_category = await category_service.create_category(category_create_request, current_user_id)
                mapping_list.append({"tableName": "categories", "tempId": operation.row_id, "serverId": real_category.id})
            elif operation.operation == "update":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "categories"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "categories")
                category_edit_request = category_schemas.CategoryUpdate.model_validate(operation.payload)
                await category_service.update_category(int(operation.row_id), category_edit_request, current_user_id)
            elif operation.operation == "delete":
                if operation.row_id in [item["tempId"] for item in mapping_list if item["tableName"] == "categories"]:
                    operation.row_id = next(item["serverId"] for item in mapping_list if item["tempId"] == operation.row_id and item["tableName"] == "categories")
                    mapping_list = [item for item in mapping_list if not (item["tableName"] == "categories" and item["serverId"] == operation.row_id)]
                await category_service.delete_category(int(operation.row_id), current_user_id)


    return ApiResponse(message="일정 변경사항을 일괄 배치하였습니다.", data=mapping_list)
