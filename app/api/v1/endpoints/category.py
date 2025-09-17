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
def get_my_categories(category_service: Annotated[CategoryService, Depends()], Authorize: AuthJWT = Depends()):
    username = Authorize.get_jwt_subject()
    categories = category_service.get_my_categories(username)
    return ApiResponse(message="카테고리 목록을 조회하였습니다.", data=categories)

@router.post("/", response_model=ApiResponse[CategoryResponse])
def create_category(request: CategoryCreate, category_service: Annotated[CategoryService, Depends()], Authorize: AuthJWT = Depends()):
    username = Authorize.get_jwt_subject()
    category = category_service.create_category(request, username)
    return ApiResponse(message="카테고리가 생성되었습니다.", data=category)

@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
def update_category(
    category_id: Annotated[int, Path(ge=1)],
    request: CategoryUpdate,
    category_service: Annotated[CategoryService, Depends()],
    Authorize: AuthJWT = Depends()
):
    username = Authorize.get_jwt_subject()
    category = category_service.update_category(category_id, request, username)
    return ApiResponse(message="카테고리가 수정되었습니다.", data=category)

@router.delete("/{category_id}", response_model=ApiResponse[None])
def delete_category(
    category_id: Annotated[int, Path(ge=1)],
    category_service: Annotated[CategoryService, Depends()],
    Authorize: AuthJWT = Depends()
):
    username = Authorize.get_jwt_subject()
    category_service.delete_category(category_id, username)
    return ApiResponse(message="카테고리가 삭제되었습니다.", data=None)
