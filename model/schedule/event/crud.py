from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload

from . import models
from ...user import models as user_models
from ...participant import models as participant_models

class EventCRUD:
    def find_by_participant_and_range(self, db: Session, user: user_models.User, start_date: date, end_date: date) -> List[models.Event]:
        # This is a simplified version, as the original query was complex, potentially involving joins
        # with Participant and then filtering events. For now, we fetch events where the user is a participant
        # and the event's date range overlaps with the given range.
        return (
            db.query(models.Event)
            .join(participant_models.Participant, models.Event.id == participant_models.Participant.event_id)
            .filter(participant_models.Participant.user_id == user.id)
            .filter(models.Event.start_date <= end_date)
            .filter(models.Event.end_date >= start_date)
            .options(joinedload(models.Event.participants).joinedload(participant_models.Participant.category))
            .all()
        )

    def get_event_by_id(self, db: Session, event_id: int) -> Optional[models.Event]:
        return db.query(models.Event).filter(models.Event.id == event_id).first()

    def get_event_by_id_with_category(self, db: Session, event_id: int, user: user_models.User) -> Optional[models.Event]:
        return (
            db.query(models.Event)
            .options(joinedload(models.Event.participants).joinedload(participant_models.Participant.category))
            .filter(models.Event.id == event_id)
            .filter(models.Event.participants.any(user_id=user.id))
            .first()
        )

    def save(self, db: Session, event: models.Event) -> models.Event:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    def delete(self, db: Session, event: models.Event) -> None:
        db.delete(event)
        db.commit()

event_crud = EventCRUD()
