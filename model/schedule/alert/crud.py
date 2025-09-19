from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from . import models
from ..participant import models as participant_models
from ..routine import models as routine_models

class AlertCRUD:
    async def delete_by_participant(self, db: AsyncSession, participant: participant_models.Participant) -> None:
        await db.execute(
            delete(models.Alert).where(models.Alert.participant_id == participant.id)
        )
        await db.commit()

    async def save(self, db: AsyncSession, alert: models.Alert) -> models.Alert:
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def find_by_participant(self, db: AsyncSession, participant: participant_models.Participant) -> List[models.Alert]:
        result = await db.execute(
            select(models.Alert).where(models.Alert.participant_id == participant.id)
        )
        return result.scalars().all()

    async def delete_by_routine(self, db: AsyncSession, routine: routine_models.Routine) -> None:
        await db.execute(
            delete(models.Alert).where(models.Alert.routine_id == routine.id)
        )
        await db.commit()

alert_crud = AlertCRUD()
