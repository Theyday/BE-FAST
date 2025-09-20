from typing import List
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from . import models
from ..user import models as user_models

class CategoryCRUD:
    async def find_by_id_and_user(self, db: AsyncSession, category_id: int, user: user_models.User) -> Optional[models.Category]:
        result = await db.execute(
            select(models.Category)
            .where(models.Category.id == category_id)
            .where(models.Category.user_id == user.id)
        )
        return result.scalars().first()
    async def find_by_user_order_by_created(self, db: AsyncSession, user: user_models.User) -> List[models.Category]:
        result = await db.execute(
            select(models.Category)
            .where(models.Category.user_id == user.id)
            .order_by(models.Category.created_at.asc())
        )
        return result.scalars().all()

    async def save(self, db: AsyncSession, category: models.Category) -> models.Category:
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    async def save_all(self, db: AsyncSession, categories: List[models.Category]) -> List[models.Category]:
        db.add_all(categories)
        await db.commit()
        for category in categories:
            await db.refresh(category)
        return categories

    async def create_default(self, db: AsyncSession, user: user_models.User) -> List[models.Category]:
        default_categories = [
            models.Category(name="취미", color="#0090FF", user_id=user.id, is_default=False),
            models.Category(name="약속", color="#32CC59", user_id=user.id, is_default=False),
            models.Category(name="내 일정", color="#FF4040", user_id=user.id, is_default=True),
        ]
        return await self.save_all(db, default_categories)

    async def find_default_category(self, db: AsyncSession, user: user_models.User) -> Optional[models.Category]:
        result = await db.execute(
            select(models.Category)
            .where(models.Category.user_id == user.id)
            .where(models.Category.is_default == True)
        )
        return result.scalars().first()
    
    async def delete(self, db: AsyncSession, category: models.Category) -> None:
        await db.delete(category)
        await db.commit()

category_crud = CategoryCRUD()
