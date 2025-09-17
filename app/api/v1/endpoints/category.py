from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi_jwt_auth import AuthJWT

from model.database import get_db
from model.response_models import ApiResponse
from model.category.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.user_service import UserService # For _load_user_by_username
from app.services.category_service import CategoryService, CustomException

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[CategoryResponse]])
def get_my_categories(user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())], category_service: Annotated[CategoryService, Depends()], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() # Verify access token validity
    categories = category_service.get_my_categories(user_id)
    return ApiResponse(message="카테고리 목록을 조회하였습니다.", data=categories)

@router.post("/", response_model=ApiResponse[CategoryResponse])
def create_category(request: CategoryCreate, user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())], category_service: Annotated[CategoryService, Depends()], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() # Verify access token validity
    category = category_service.create_category(request, user_id)
    return ApiResponse(message="카테고리가 생성되었습니다.", data=category)

@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
def update_category(
    category_id: Annotated[int, Path(ge=1)],
    request: CategoryUpdate,
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    category_service: Annotated[CategoryService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    category = category_service.update_category(category_id, request, user_id)
    return ApiResponse(message="카테고리가 수정되었습니다.", data=category)

@router.delete("/{category_id}", response_model=ApiResponse[None])
def delete_category(
    category_id: Annotated[int, Path(ge=1)],
    user_id: Annotated[int, Depends(lambda Authorize: Authorize.get_jwt_subject())],
    category_service: Annotated[CategoryService, Depends()],
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required() # Verify access token validity
    category_service.delete_category(category_id, user_id)
    return ApiResponse(message="카테고리가 삭제되었습니다.", data=None)
