from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import case, func, and_, cast, Date

from . import models
from model.user import models as user_models
from model.schedule.participant import models as participant_models

class TaskCRUD:
    def find_uncompleted_tasks_by_participant_and_range(self, db: Session, user: user_models.User, start_date: date, end_date: date) -> List[models.Task]:
        Task = models.Task
        Participant = participant_models.Participant
        start_time_expr = func.coalesce(
            Task.start_time,
            case(
                (Task.created_at > Task.end_time, Task.end_time),
                else_=Task.created_at
            )
        )
        end_time_expr = func.coalesce(
            Task.end_time,
            func.to_timestamp('9999-12-31', 'YYYY-MM-DD')
        )
        date_overlap = and_(
            cast(start_time_expr, Date) <= end_date,
            cast(end_time_expr, Date) >= start_date
        )
        return (
            db.query(Task)
            .join(Participant, Task.id == Participant.task_id)
            .filter(Participant.user_id == user.id)
            .filter(Task.is_completed == False)
            .filter(date_overlap)
            .options(joinedload(Task.participants).joinedload(Participant.category))
            .all()
        )

    def find_completed_tasks_by_participant_and_range(self, db: Session, user: user_models.User, start_date: date, end_date: date) -> List[models.Task]:
        """
        완료된 Task들을 조회하는 메소드
        - 참가자(user) 기준
        - 완료된 Task만
        - completed_at 기준으로 날짜 범위 필터
        """
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
        """ID로 Task 조회"""
        return db.query(models.Task).filter(models.Task.id == task_id).first()

    def get_task_by_id_with_category(self, db: Session, task_id: int, user: user_models.User) -> Optional[models.Task]:
        """ID로 Task 조회 (카테고리 정보 포함, 사용자 권한 체크)"""
        return (
            db.query(models.Task)
            .options(joinedload(models.Task.participants).joinedload(participant_models.Participant.category))
            .filter(models.Task.id == task_id)
            .filter(models.Task.participants.any(user_id=user.id))
            .first()
        )

    def save(self, db: Session, task: models.Task) -> models.Task:
        """Task 저장"""
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task: models.Task) -> None:
        """Task 삭제"""
        db.delete(task)
        db.commit()

task_crud = TaskCRUD()
