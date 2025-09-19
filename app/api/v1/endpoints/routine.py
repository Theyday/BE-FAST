from fastapi import APIRouter, Depends, Path
from typing import Annotated, List, Optional
from fastapi_jwt_auth import AuthJWT

from model.response_models import ApiResponse
from model.schedule.routine.schemas import RoutineCreateRequest, RoutineResponse
from app.services.user_service import UserService # To get user from subject
from app.services.routine_service import RoutineService, CustomException

router = APIRouter()

@router.post("", response_model=ApiResponse[None])
def create_routine(
    request: RoutineCreateRequest,
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    routine_service.create_routine(request, username)
    return ApiResponse(message="루틴을 생성하였습니다.", data=None)

@router.put("/{routine_id}", response_model=ApiResponse[None])
def update_routine(
    routine_id: Annotated[int, Path(ge=1)],
    request: RoutineCreateRequest,
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    routine_service.update_routine(routine_id, request, username)
    return ApiResponse(message="루틴을 수정하였습니다.", data=None)

@router.get("", response_model=ApiResponse[List[RoutineResponse]])
def get_my_routines(
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    routines = routine_service.get_my_routines(username)
    return ApiResponse(message="내 루틴 목록을 조회하였습니다.", data=routines)

@router.get("/{routine_id}", response_model=ApiResponse[RoutineResponse])
def get_routine(
    routine_id: Annotated[int, Path(ge=1)],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    routine = routine_service.get_routine(routine_id)
    return ApiResponse(message="루틴을 조회하였습니다.", data=routine)

@router.delete("/{routine_id}", response_model=ApiResponse[None])
def delete_routine(
    routine_id: Annotated[int, Path(ge=1)],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    routine_service.delete_routine(routine_id, username)
    return ApiResponse(message="루틴을 삭제하였습니다.", data=None)
