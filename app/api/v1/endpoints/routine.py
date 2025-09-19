from fastapi import APIRouter, Depends, Path
from typing import Annotated, List
from core.jwt_security import get_current_user_id

from model.response_models import ApiResponse
from model.schedule.routine.schemas import RoutineCreateRequest, RoutineResponse
from app.services.routine_service import RoutineService

router = APIRouter()

@router.post("", response_model=ApiResponse[None])
async def create_routine(
    request: RoutineCreateRequest,
    routine_service: Annotated[RoutineService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await routine_service.create_routine(request, current_user_id)
    return ApiResponse(message="루틴을 생성하였습니다.", data=None)

@router.put("/{routine_id}", response_model=ApiResponse[None])
async def update_routine(
    routine_id: Annotated[int, Path(ge=1)],
    request: RoutineCreateRequest,
    routine_service: Annotated[RoutineService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await routine_service.update_routine(routine_id, request, current_user_id)
    return ApiResponse(message="루틴을 수정하였습니다.", data=None)

@router.get("", response_model=ApiResponse[List[RoutineResponse]])
async def get_my_routines(
    routine_service: Annotated[RoutineService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    routines = await routine_service.get_my_routines(current_user_id)
    return ApiResponse(message="내 루틴 목록을 조회하였습니다.", data=routines)

@router.get("/{routine_id}", response_model=ApiResponse[RoutineResponse])
async def get_routine(
    routine_id: Annotated[int, Path(ge=1)],
    routine_service: Annotated[RoutineService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    routine = await routine_service.get_routine(routine_id, current_user_id)
    return ApiResponse(message="루틴을 조회하였습니다.", data=routine)

@router.delete("/{routine_id}", response_model=ApiResponse[None])
async def delete_routine(
    routine_id: Annotated[int, Path(ge=1)],
    routine_service: Annotated[RoutineService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    await routine_service.delete_routine(routine_id, current_user_id)
    return ApiResponse(message="루틴을 삭제하였습니다.", data=None)
