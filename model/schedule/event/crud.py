from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from . import models
from model.user import models as user_models
from model.schedule.participant import models as participant_models

class EventCRUD:
    async def find_by_participant_and_range(
        self, db: AsyncSession, user: user_models.User, start_date: date, end_date: date
    ) -> List[models.Event]:
        stmt = (
            select(models.Event)
            .join(models.Event.participants)
            .join(participant_models.Participant.category)
            .where(participant_models.Participant.user_id == user.id)
            .where(models.Event.start_date <= end_date)
            .where(models.Event.end_date >= start_date)
            .options(
                joinedload(models.Event.participants).joinedload(participant_models.Participant.category)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def get_event_by_id(self, db: AsyncSession, event_id: int) -> Optional[models.Event]:
        stmt = select(models.Event).where(models.Event.id == event_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_event_by_id_with_category(
        self, db: AsyncSession, event_id: int, user: user_models.User
    ) -> Optional[models.Event]:
        stmt = (
            select(models.Event)
            .options(joinedload(models.Event.participants).joinedload(participant_models.Participant.category))
            .where(models.Event.id == event_id)
            .where(models.Event.participants.any(user_id=user.id))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def save(self, db: AsyncSession, event: models.Event) -> models.Event:
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    async def delete(self, db: AsyncSession, event: models.Event) -> None:
        await db.delete(event)
        await db.commit()

event_crud = EventCRUD()
