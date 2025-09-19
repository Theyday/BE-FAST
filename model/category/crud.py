from typing import List

from sqlalchemy.orm import Session

from . import models
from ..user import models as user_models

class CategoryCRUD:
    def find_by_user_order_by_created(self, db: Session, user: user_models.User) -> List[models.Category]:
        return (
            db.query(models.Category)
            .filter(models.Category.user_id == user.id)
            .order_by(models.Category.created_at.asc())
            .all()
        )

    def save(self, db: Session, category: models.Category) -> models.Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def save_all(self, db: Session, categories: List[models.Category]) -> List[models.Category]:
        db.add_all(categories)
        db.commit()
        for category in categories:
            db.refresh(category)
        return categories

    def create_default(self, db: Session, user: user_models.User) -> List[models.Category]:
        default_categories = [
            models.Category(name="취미", color="#0090FF", user_id=user.id, is_default=False),
            models.Category(name="약속", color="#32CC59", user_id=user.id, is_default=False),
            models.Category(name="내 일정", color="#FF4040", user_id=user.id, is_default=True),
        ]
        return self.save_all(db, default_categories)

category_crud = CategoryCRUD()
