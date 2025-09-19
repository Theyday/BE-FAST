from fastapi import APIRouter, Depends, Path
from typing import Annotated, List

from model.response_models import ApiResponse
from model.category.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from core.jwt_security import get_current_user_id

router = APIRouter()

@router.get("", response_model=ApiResponse[List[CategoryResponse]])
def get_my_categories(
    category_service: Annotated[CategoryService, Depends()], 
    current_user_id: int = Depends(get_current_user_id)
):
    username = current_user_id
    categories = category_service.get_my_categories(username)
    return ApiResponse(message="카테고리 목록을 조회하였습니다.", data=categories)

@router.post("", response_model=ApiResponse[CategoryResponse])
def create_category(request: CategoryCreate, category_service: Annotated[CategoryService, Depends()], current_user_id: int = Depends(get_current_user_id)):
    username = current_user_id
    category = category_service.create_category(request, username)
    return ApiResponse(message="카테고리가 생성되었습니다.", data=category)

@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
def update_category(
    category_id: Annotated[int, Path(ge=1)],
    request: CategoryUpdate,
    category_service: Annotated[CategoryService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    username = current_user_id
    category = category_service.update_category(category_id, request, username)
    return ApiResponse(message="카테고리가 수정되었습니다.", data=category)

@router.delete("/{category_id}", response_model=ApiResponse[None])
def delete_category(
    category_id: Annotated[int, Path(ge=1)],
    category_service: Annotated[CategoryService, Depends()],
    current_user_id: int = Depends(get_current_user_id)
):
    category_service.delete_category(category_id, current_user_id)
    return ApiResponse(message="카테고리가 삭제되었습니다.", data=None)
