from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import datetime

from . import models
from ...user import models as user_models

class RoutineCRUD:
    async def create_default_routines_for_user(self, db: AsyncSession, user: user_models.User) -> List[models.Routine]:
        default_routines = [
            models.Routine(
                user_id=user.id,
                name="수면",
                days_of_week="0,1,2,3,4,5,6",
                start_time=datetime.time(23, 0, 0),
                end_time=datetime.time(7, 0, 0),
                icon="moon",
                color="#8E8E93"
            ),
            models.Routine(
                user_id=user.id,
                name="업무",
                days_of_week="1,2,3,4,5",
                start_time=datetime.time(9, 0, 0),
                end_time=datetime.time(12, 30, 0),
                icon="briefcase",
                color="#0090FF"
            ),
        ]
        db.add_all(default_routines)
        await db.commit()
        for routine in default_routines:
            await db.refresh(routine)
        return default_routines

    async def get_routine_by_id(self, db: AsyncSession, routine_id: int) -> Optional[models.Routine]:
        result = await db.execute(
            select(models.Routine)
            .options(joinedload(models.Routine.alerts))
            .where(models.Routine.id == routine_id)
        )
        return result.scalars().first()

    async def find_by_user_with_alerts(self, db: AsyncSession, user: user_models.User) -> List[models.Routine]:
        result = await db.execute(
            select(models.Routine)
            .where(models.Routine.user_id == user.id)
            .options(joinedload(models.Routine.alerts))
        )
        return result.scalars().unique().all()

    async def save(self, db: AsyncSession, routine: models.Routine) -> models.Routine:
        db.add(routine)
        await db.commit()
        await db.refresh(routine)
        return routine

    async def delete(self, db: AsyncSession, routine: models.Routine) -> None:
        await db.delete(routine)
        await db.commit()

routine_crud = RoutineCRUD()
