from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models
from ...category import models as category_models
from ...user import models as user_models
from ...schedule.event import models as event_models
from ...schedule.task import models as task_models

class ParticipantCRUD:
    async def find_by_category(self, db: AsyncSession, category: category_models.Category) -> List[models.Participant]:
        result = await db.execute(
            select(models.Participant).where(models.Participant.category_id == category.id)
        )
        return result.scalars().all()

    async def save(self, db: AsyncSession, participant: models.Participant) -> models.Participant:
        db.add(participant)
        await db.commit()
        await db.refresh(participant)
        return participant

    async def find_by_event_and_participant(self, db: AsyncSession, event: event_models.Event, user: user_models.User) -> Optional[models.Participant]:
        result = await db.execute(
            select(models.Participant).where(
                models.Participant.event_id == event.id,
                models.Participant.user_id == user.id
            )
        )
        return result.scalars().first()

    async def find_by_task_and_participant(self, db: AsyncSession, task: task_models.Task, user: user_models.User) -> Optional[models.Participant]:
        result = await db.execute(
            select(models.Participant).where(
                models.Participant.task_id == task.id,
                models.Participant.user_id == user.id
            )
        )
        return result.scalars().first()

participant_crud = ParticipantCRUD()
