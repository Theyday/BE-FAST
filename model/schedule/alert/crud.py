from typing import List, Optional

from sqlalchemy.orm import Session

from . import models
from ..participant import models as participant_models
from ..routine import models as routine_models

class AlertCRUD:
    def delete_by_participant(self, db: Session, participant: participant_models.Participant) -> None:
        db.query(models.Alert).filter(models.Alert.participant_id == participant.id).delete()
        db.commit()

    def save(self, db: Session, alert: models.Alert) -> models.Alert:
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    def find_by_participant(self, db: Session, participant: participant_models.Participant) -> List[models.Alert]:
        return db.query(models.Alert).filter(models.Alert.participant_id == participant.id).all()
    
    def delete_by_routine(self, db: Session, routine: routine_models.Routine) -> None:
        db.query(models.Alert).filter(models.Alert.routine_id == routine.id).delete()
        db.commit()

alert_crud = AlertCRUD()
