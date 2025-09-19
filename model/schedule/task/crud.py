from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func, and_, cast, Date
from sqlalchemy.orm import joinedload

from . import models
from model.user import models as user_models
from model.schedule.participant import models as participant_models

class TaskCRUD:
    async def find_uncompleted_tasks_by_participant_and_range(
        self, db: AsyncSession, user: user_models.User, start_date: date, end_date: date
    ) -> List[models.Task]:
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

        stmt = (
            select(Task)
            .join(Participant, Task.id == Participant.task_id)
            .filter(Participant.user_id == user.id)
            .filter(Task.is_completed == False)
            .filter(date_overlap)
            .options(joinedload(Task.participants).joinedload(Participant.category))
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def find_completed_tasks_by_participant_and_range(
        self, db: AsyncSession, user: user_models.User, start_date: date, end_date: date
    ) -> List[models.Task]:
        Task = models.Task
        Participant = participant_models.Participant

        stmt = (
            select(Task)
            .join(Participant, Task.id == Participant.task_id)
            .filter(Participant.user_id == user.id)
            .filter(Task.is_completed == True)
            .filter(Task.completed_at >= start_date)
            .filter(Task.completed_at <= end_date)
            .options(joinedload(Task.participants).joinedload(Participant.category))
        )
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def get_task_by_id(self, db: AsyncSession, task_id: int) -> Optional[models.Task]:
        """ID로 Task 조회"""
        stmt = select(models.Task).filter(models.Task.id == task_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_task_by_id_with_category(
        self, db: AsyncSession, task_id: int, user: user_models.User
    ) -> Optional[models.Task]:
        """ID로 Task 조회 (카테고리 정보 포함, 사용자 권한 체크)"""
        stmt = (
            select(models.Task)
            .options(joinedload(models.Task.participants).joinedload(participant_models.Participant.category))
            .filter(models.Task.id == task_id)
            .filter(models.Task.participants.any(user_id=user.id))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def save(self, db: AsyncSession, task: models.Task) -> models.Task:
        """Task 저장"""
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def delete(self, db: AsyncSession, task: models.Task) -> None:
        """Task 삭제"""
        await db.delete(task)
        await db.commit()

task_crud = TaskCRUD()
