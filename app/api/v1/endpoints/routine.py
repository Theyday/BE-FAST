from fastapi import APIRouter, Depends, Path
from typing import Annotated, List, Optional
from fastapi_jwt_auth import AuthJWT

from ....model.response_models import ApiResponse
from ....model.schedule.routine.schemas import RoutineCreateRequest, RoutineResponse
from ....app.services.user_service import UserService # To get user from subject
from ....app.services.routine_service import RoutineService, CustomException

router = APIRouter()

@router.post("/", response_model=ApiResponse[None])
def create_routine(
    request: RoutineCreateRequest,
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    routine_service.create_routine(request, user_id)
    return ApiResponse(message="루틴을 생성하였습니다.", data=None)

@router.put("/{routine_id}", response_model=ApiResponse[None])
def update_routine(
    routine_id: Annotated[int, Path(ge=1, alias="routineId")],
    request: RoutineCreateRequest,
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    routine_service.update_routine(routine_id, request, user_id)
    return ApiResponse(message="루틴을 수정하였습니다.", data=None)

@router.get("/", response_model=ApiResponse[List[RoutineResponse]])
def get_my_routines(
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    routines = routine_service.get_my_routines(user_id)
    return ApiResponse(message="내 루틴 목록을 조회하였습니다.", data=routines)

@router.get("/{routine_id}", response_model=ApiResponse[RoutineResponse])
def get_routine(
    routine_id: Annotated[int, Path(ge=1, alias="routineId")],
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    routine = routine_service.get_routine(routine_id)
    return ApiResponse(message="루틴을 조회하였습니다.", data=routine)

@router.delete("/{routine_id}", response_model=ApiResponse[None])
def delete_routine(
    routine_id: Annotated[int, Path(ge=1, alias="routineId")],
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    routine_service: Annotated[RoutineService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    routine_service.delete_routine(routine_id, user_id)
    return ApiResponse(message="루틴을 삭제하였습니다.", data=None)
