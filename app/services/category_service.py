from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from model.database import get_async_session
from model.user.crud import user_crud
from model.category.crud import category_crud
from model.schedule.participant.crud import participant_crud
from model.user import models as user_models
from model.category import models as category_models
from model.category import schemas as category_schemas

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class CategoryService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_async_session),
        ):
        self.db = db

    async def get_my_categories(self, current_user_id: int) -> List[category_schemas.CategoryResponse]:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # In Spring Boot, it was `findByUserOrderByRecentActivity`, which implies a custom ordering logic.
        # For now, let's just get by user and then sort in Python. Actual `recentActivity` would need to be tracked.
        categories = await category_crud.find_by_user_order_by_created(self.db, user)

        sorted_categories = sorted(categories, key=lambda c: (not c.is_default, c.id))

        result = []
        for c in sorted_categories:
            result.append(category_schemas.CategoryResponse(
                id=c.id,
                name=c.name,
                color=c.color,
                isDefault=c.is_default
            ))
        return result

    async def create_category(self, request: category_schemas.CategoryCreate, current_user_id: int) -> category_schemas.CategoryResponse:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        category = category_models.Category(
            name=request.name,
            color=request.color,
            user_id=user.id,
            is_default=False
        )
        saved_category = await category_crud.save(self.db, category)
        return category_schemas.CategoryResponse(
            id=saved_category.id,
            name=saved_category.name,
            color=saved_category.color,
            isDefault=saved_category.is_default
        )

    async def update_category(self, category_id: int, request: category_schemas.CategoryUpdate, current_user_id: int) -> category_schemas.CategoryResponse:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        category = await category_crud.find_by_id_and_user(self.db, category_id, user)
        if not category:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
        category.name = request.name
        category.color = request.color
        updated_category = await category_crud.save(self.db, category)
        return category_schemas.CategoryResponse(
            id=updated_category.id,
            name=updated_category.name,
            color=updated_category.color,
            isDefault=updated_category.is_default
        )

    async def delete_category(self, category_id: int, current_user_id: int) -> None:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        category_to_delete = await category_crud.find_by_id_and_user(self.db, category_id, user)
        if not category_to_delete:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Find default category
        default_category = await self.find_default_category(user)
        if default_category is None: # Should not happen if createDefault is called on user creation
            raise CustomException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default category not found")

        # Reassign participants to default category
        participants_to_reassign = await participant_crud.find_by_category(self.db, category_to_delete)
        for participant in participants_to_reassign:
            participant.category = default_category
            await participant_crud.save(self.db, participant)

        await category_crud.delete(self.db, category_to_delete)

    async def find_default_category(self, user: user_models.User) -> Optional[category_models.Category]:
        return await category_crud.find_default_category(self.db, user)
