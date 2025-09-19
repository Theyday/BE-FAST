from fastapi import APIRouter, Depends, Path, Query
from typing import Annotated, Optional
from datetime import date
from fastapi_jwt_auth import AuthJWT

from model.response_models import ApiResponse
from model.schedule.task.schemas import TaskDetailResponse, TaskEditRequest, ScheduleTaskRequest, TaskResponse
from app.services.user_service import UserService # To get user from subject
from app.services.task_service import TaskService, CustomException

router = APIRouter()

@router.get("/{task_id}", response_model=ApiResponse[TaskDetailResponse])
def get_task_detail(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    task = task_service.get_task_detail(task_id, username)
    return ApiResponse(message="작업을 조회하였습니다.", data=task)

@router.put("/{task_id}", response_model=ApiResponse[None])
def edit_task(
    task_id: Annotated[int, Path(ge=1)],
    request: TaskEditRequest,
    task_service: Annotated[TaskService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    task_service.edit_task(task_id, request, username)
    return ApiResponse(message="작업을 수정하였습니다.", data=None)

@router.delete("/{task_id}", response_model=ApiResponse[None])
def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    task_service.delete_task(task_id, username)
    return ApiResponse(message="작업을 삭제하였습니다.", data=None)

@router.put("/{task_id}/schedule", response_model=ApiResponse[None])
def schedule_task(
    task_id: Annotated[int, Path(ge=1)],
    request: ScheduleTaskRequest,
    task_service: Annotated[TaskService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    task_service.schedule_task(task_id, request, username)
    return ApiResponse(message="작업을 일정에 추가하였습니다.", data=None)

@router.put("/{task_id}/complete", response_model=ApiResponse[None])
def toggle_task_complete(
    task_id: Annotated[int, Path(ge=1)],
    date: Annotated[date, Query(alias="date")],
    task_service: Annotated[TaskService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    task_service.toggle_task_complete(task_id, date, username)
    return ApiResponse(message="작업을 완료하였습니다.", data=None)
