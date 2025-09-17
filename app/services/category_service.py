from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from model.database import get_db
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
        db: Session = Depends(get_db),
    ):
        self.db = db

    def get_my_categories(self, user_id: int) -> List[category_schemas.CategoryResponse]:
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # In Spring Boot, it was `findByUserOrderByRecentActivity`, which implies a custom ordering logic.
        # For now, let's just get by user and then sort in Python. Actual `recentActivity` would need to be tracked.
        categories = self.db.query(category_models.Category).filter(category_models.Category.user_id == user.id).all()

        # Sort default categories to the front, then by other criteria if needed
        sorted_categories = sorted(categories, key=lambda c: (not c.is_default, c.id)) # Sort by is_default (false first), then by id
        
        return [category_schemas.CategoryResponse.model_validate(c) for c in sorted_categories]

    def create_category(self, request: category_schemas.CategoryCreate, user_id: int) -> category_schemas.CategoryResponse:
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        category = category_models.Category(
            name=request.name,
            color=request.color,
            user_id=user.id,
            is_default=False
        )
        saved_category = category_crud.save(self.db, category)
        return category_schemas.CategoryResponse.model_validate(saved_category)

    def update_category(self, category_id: int, request: category_schemas.CategoryUpdate, user_id: int) -> category_schemas.CategoryResponse:
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        category = self.db.query(category_models.Category).filter(
            category_models.Category.id == category_id, 
            category_models.Category.user_id == user.id
        ).first()
        if not category:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
        category.name = request.name
        category.color = request.color
        updated_category = category_crud.save(self.db, category)
        return category_schemas.CategoryResponse.model_validate(updated_category)

    def delete_category(self, category_id: int, user_id: int) -> None:
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        category_to_delete = self.db.query(category_models.Category).filter(
            category_models.Category.id == category_id, 
            category_models.Category.user_id == user.id
        ).first()
        if not category_to_delete:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Find default category
        default_category = self.find_default_category(user)
        if default_category is None: # Should not happen if createDefault is called on user creation
            raise CustomException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default category not found")

        # Reassign participants to default category
        participants_to_reassign = participant_crud.find_by_category(self.db, category_to_delete)
        for participant in participants_to_reassign:
            participant.category = default_category
            participant_crud.save(self.db, participant)

        self.db.delete(category_to_delete)
        self.db.commit()

    def find_default_category(self, user: user_models.User) -> Optional[category_models.Category]:
        return self.db.query(category_models.Category).filter(
            category_models.Category.user_id == user.id,
            category_models.Category.is_default == True
        ).first()
