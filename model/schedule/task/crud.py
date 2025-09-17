from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload

from . import models
from model.user import models as user_models
from model.schedule.participant import models as participant_models

class TaskCRUD:
    def find_uncompleted_tasks_by_participant_and_range(self, db: Session, user: user_models.User, start_date: date, end_date: date) -> List[models.Task]:
        # This is a simplified version, as the original query was complex, potentially involving joins
        # with Participant and then filtering tasks. For now, we fetch tasks where the user is a participant
        # and the task's date range overlaps with the given range, and is_completed is false.
        return (
            db.query(models.Task)
            .join(participant_models.Participant, models.Task.id == participant_models.Participant.task_id)
            .filter(participant_models.Participant.user_id == user.id)
            .filter(models.Task.is_completed == False)
            .filter(models.Task.start_time <= end_date.isoformat() + " 23:59:59")  # Compare with end of day
            .filter(models.Task.end_time >= start_date.isoformat() + " 00:00:00")  # Compare with start of day
            .options(joinedload(models.Task.participants).joinedload(participant_models.Participant.category))
            .all()
        )

    def find_completed_tasks_by_participant_and_range(self, db: Session, user: user_models.User, start_date: date, end_date: date) -> List[models.Task]:
        # Similar to uncompleted tasks, but with is_completed is true.
        return (
            db.query(models.Task)
            .join(participant_models.Participant, models.Task.id == participant_models.Participant.task_id)
            .filter(participant_models.Participant.user_id == user.id)
            .filter(models.Task.is_completed == True)
            .filter(models.Task.completed_at >= start_date)
            .filter(models.Task.completed_at <= end_date)
            .options(joinedload(models.Task.participants).joinedload(participant_models.Participant.category))
            .all()
        )

    def get_task_by_id(self, db: Session, task_id: int) -> Optional[models.Task]:
        return db.query(models.Task).filter(models.Task.id == task_id).first()

    def get_task_by_id_with_category(self, db: Session, task_id: int, user: user_models.User) -> Optional[models.Task]:
        return (
            db.query(models.Task)
            .options(joinedload(models.Task.participants).joinedload(participant_models.Participant.category))
            .filter(models.Task.id == task_id)
            .filter(models.Task.participants.any(user_id=user.id))
            .first()
        )

    def save(self, db: Session, task: models.Task) -> models.Task:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task: models.Task) -> None:
        db.delete(task)
        db.commit()

task_crud = TaskCRUD()
