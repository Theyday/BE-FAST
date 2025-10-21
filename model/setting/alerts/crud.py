from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from . import models
from . import schemas
from datetime import datetime

class AlertCRUD:
    async def create_default_alert_setting(self, db: AsyncSession, user_id: int) -> models.UserAlert:
        default_alert = models.UserAlert(
            user_id=user_id,
            event_start=10,
            task_end=60*24,
            routine_start=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(default_alert)
        await db.commit()
        await db.refresh(default_alert)
        return default_alert

    async def get_alert_setting_by_id(self, db: AsyncSession, alert_id: int) -> Optional[models.UserAlert]:
        result = await db.execute(
            select(models.UserAlert)
            .where(models.UserAlert.id == alert_id)
        )
        return result.scalars().first()

    async def get_alert_setting_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[models.UserAlert]:
        result = await db.execute(
            select(models.UserAlert)
            .where(models.UserAlert.user_id == user_id)
        )
        return result.scalars().first()

    async def update_alert_setting(self, db: AsyncSession, alert_id: int, new_settings: dict) -> Optional[models.UserAlert]:
        alert = await self.get_alert_setting_by_id(db, alert_id)
        if alert:
            for key, value in new_settings.items():
                setattr(alert, key, value)
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
        return alert

    async def save(self, db: AsyncSession, alert: models.UserAlert) -> models.UserAlert:
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    # async def delete(self, db: AsyncSession, alert: models.UserAlert) -> None:
    #     await db.delete(alert)
    #     await db.commit()

alert_crud = AlertCRUD()