from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from . import models
from ...user import models as user_models

class RoutineCRUD:
    def create_default_routines_for_user(self, db: Session, user: user_models.User) -> List[models.Routine]:
        default_routines = [
            models.Routine(user_id=user.id, name="수면", days_of_week="0,1,2,3,4,5,6", start_time="23:00:00", end_time="07:00:00", icon="moon", color="#8E8E93"),
            models.Routine(user_id=user.id, name="업무", days_of_week="1,2,3,4,5", start_time="09:00:00", end_time="12:30:00", icon="briefcase", color="#0090FF"),
        ]
        db.add_all(default_routines)
        db.commit()
        for routine in default_routines:
            db.refresh(routine)
        return default_routines

    def get_routine_by_id(self, db: Session, routine_id: int) -> Optional[models.Routine]:
        return db.query(models.Routine).filter(models.Routine.id == routine_id).first()

    def find_by_user_with_alerts(self, db: Session, user: user_models.User) -> List[models.Routine]:
        return (
            db.query(models.Routine)
            .filter(models.Routine.user_id == user.id)
            .options(joinedload(models.Routine.alerts))
            .all()
        )

    def save(self, db: Session, routine: models.Routine) -> models.Routine:
        db.add(routine)
        db.commit()
        db.refresh(routine)
        return routine

    def delete_by_id(self, db: Session, routine_id: int) -> None:
        db.query(models.Routine).filter(models.Routine.id == routine_id).delete()
        db.commit()

routine_crud = RoutineCRUD()
