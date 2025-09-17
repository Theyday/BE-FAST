from typing import List, Optional

from sqlalchemy.orm import Session

from . import models
from ...category import models as category_models
from ...user import models as user_models
from ...schedule.event import models as event_models
from ...schedule.task import models as task_models

class ParticipantCRUD:
    def find_by_category(self, db: Session, category: category_models.Category) -> List[models.Participant]:
        return db.query(models.Participant).filter(models.Participant.category_id == category.id).all()

    def save(self, db: Session, participant: models.Participant) -> models.Participant:
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant
    
    def find_by_event_and_participant(self, db: Session, event: event_models.Event, user: user_models.User) -> Optional[models.Participant]:
        return db.query(models.Participant).filter(
            models.Participant.event_id == event.id,
            models.Participant.user_id == user.id
        ).first()
    
    def find_by_task_and_participant(self, db: Session, task: task_models.Task, user: user_models.User) -> Optional[models.Participant]:
        return db.query(models.Participant).filter(
            models.Participant.task_id == task.id,
            models.Participant.user_id == user.id
        ).first()

participant_crud = ParticipantCRUD()
