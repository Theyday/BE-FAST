from fastapi import APIRouter, Depends, Path, Query
from typing import Annotated
from datetime import date

from model.response_models import ApiResponse
from model.schedule.task.schemas import TaskDetailResponse, TaskEditRequest, ScheduleTaskRequest
from app.services.task_service import TaskService
from core.jwt_security import get_current_user_id

router = APIRouter()

@router.get("/{task_id}", response_model=ApiResponse[TaskDetailResponse])
async def get_task_detail(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    task = await task_service.get_task_detail(task_id, current_user_id)
    return ApiResponse(message="작업을 조회하였습니다.", data=task)

@router.put("/{task_id}", response_model=ApiResponse[None])
async def edit_task(
    task_id: Annotated[int, Path(ge=1)],
    request: TaskEditRequest,
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await task_service.edit_task(task_id, request, current_user_id)
    return ApiResponse(message="작업을 수정하였습니다.", data=None)

@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await task_service.delete_task(task_id, current_user_id)
    return ApiResponse(message="작업을 삭제하였습니다.", data=None)

@router.put("/{task_id}/schedule", response_model=ApiResponse[None])
async def schedule_task(
    task_id: Annotated[int, Path(ge=1)],
    request: ScheduleTaskRequest,
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await task_service.schedule_task(task_id, request, current_user_id)
    return ApiResponse(message="작업을 일정에 추가하였습니다.", data=None)

@router.put("/{task_id}/complete", response_model=ApiResponse[None])
async def toggle_task_complete(
    task_id: Annotated[int, Path(ge=1)],
    date: Annotated[date, Query(alias="date")],
    task_service: Annotated[TaskService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await task_service.toggle_task_complete(task_id, date, current_user_id)
    return ApiResponse(message="작업을 완료하였습니다.", data=None)
