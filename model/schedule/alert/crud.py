from typing import List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_

from . import models
from ..event import models as event_models
from ..participant import models as participant_models
from ..routine import models as routine_models
from ..task import models as task_models
from sqlalchemy import func, DateTime, Interval, case
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import literal_column
from model.user import models as user_models

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

    async def find_event_alerts_to_send(self, db: AsyncSession, now: datetime) -> List[models.Alert]:
        """
        Java AlertRepository의 findEventAlertsToSend와 동일한 로직으로 구현
        minutes_before를 고려하여 정확한 알림 시간을 계산하고 현재 시간과 매칭
        """
        # 현재 시간을 분 단위로 문자열 변환 (Java 쿼리와 동일한 형식)
        now_str = now.strftime("%Y-%m-%d %H:%M")
        
        # EVENT_START 알림 조건
        event_start_condition = and_(
            models.Alert.type == "EVENT_START",
            or_(
                # start_time이 있는 경우
                and_(
                    event_models.Event.start_time.is_not(None),
                    func.to_char(
                        func.cast(event_models.Event.start_date, DateTime) +
                        func.cast(event_models.Event.start_time, Interval) -
                        func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                        "YYYY-MM-DD HH24:MI"
                    ) == now_str
                ),
                # start_time이 null인 경우 (00:00:00으로 처리)
                and_(
                    event_models.Event.start_time.is_(None),
                    func.to_char(
                        func.cast(event_models.Event.start_date, DateTime) +
                        literal_column("'00:00:00'::interval") -
                        func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                        "YYYY-MM-DD HH24:MI"
                    ) == now_str
                )
            )
        )
        
        # EVENT_END 알림 조건
        event_end_condition = and_(
            models.Alert.type == "EVENT_END",
            or_(
                # end_time이 있는 경우
                and_(
                    event_models.Event.end_time.is_not(None),
                    func.to_char(
                        func.cast(event_models.Event.end_date, DateTime) +
                        func.cast(event_models.Event.end_time, Interval) -
                        func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                        "YYYY-MM-DD HH24:MI"
                    ) == now_str
                ),
                # end_time이 null인 경우 (다음날 00:00:00으로 처리)
                and_(
                    event_models.Event.end_time.is_(None),
                    func.to_char(
                        func.cast(event_models.Event.end_date, DateTime) +
                        literal_column("'1 day'::interval") +
                        literal_column("'00:00:00'::interval") -
                        func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                        "YYYY-MM-DD HH24:MI"
                    ) == now_str
                )
            )
        )

        # 최종 쿼리 실행
        result = await db.execute(
            select(models.Alert)
            .join(models.Alert.participant)
            .join(participant_models.Participant.event)
            .options(
                joinedload(models.Alert.participant).joinedload(participant_models.Participant.user).joinedload(user_models.User.device_tokens),
                joinedload(models.Alert.participant).joinedload(participant_models.Participant.event),
            )
            .where(
                models.Alert.type.in_(["EVENT_START", "EVENT_END"]),
                or_(event_start_condition, event_end_condition)
            )
        )
        return result.scalars().unique().all()

    async def find_task_alerts_to_send(self, db: AsyncSession, now: datetime) -> List[models.Alert]:
        """
        Task 알림을 minutes_before를 고려하여 정확한 시간 계산으로 조회
        Java 로직과 동일하게 구현
        """
        # 현재 시간을 분 단위로 문자열 변환
        now_str = now.strftime("%Y-%m-%d %H:%M")
        
        # TASK_SCHEDULE, TASK_START, TASK_END 각각의 조건을 minutes_before를 고려하여 계산
        task_schedule_condition = and_(
            models.Alert.type == "TASK_SCHEDULE",
            func.to_char(
                func.cast(task_models.Task.scheduled_time, DateTime) -
                func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                "YYYY-MM-DD HH24:MI"
            ) == now_str
        )
        
        task_start_condition = and_(
            models.Alert.type == "TASK_START",
            func.to_char(
                func.cast(task_models.Task.start_time, DateTime) -
                func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                "YYYY-MM-DD HH24:MI"
            ) == now_str
        )
        
        task_end_condition = and_(
            models.Alert.type == "TASK_END",
            func.to_char(
                func.cast(task_models.Task.end_time, DateTime) -
                func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                "YYYY-MM-DD HH24:MI"
            ) == now_str
        )

        result = await db.execute(
            select(models.Alert)
            .join(models.Alert.participant)
            .join(participant_models.Participant.task)
            .options(
                joinedload(models.Alert.participant).joinedload(participant_models.Participant.user).joinedload(user_models.User.device_tokens),
                joinedload(models.Alert.participant).joinedload(participant_models.Participant.task),
            )
            .where(
                models.Alert.type.in_(["TASK_SCHEDULE", "TASK_START", "TASK_END"]),
                or_(task_schedule_condition, task_start_condition, task_end_condition)
            )
        )
        return result.scalars().unique().all()

    async def find_routine_alerts_to_send(self, db: AsyncSession, now: datetime) -> List[models.Alert]:
        """
        Routine 알림을 minutes_before를 고려하여 정확한 시간 계산으로 조회
        시간만 비교하는 것이 아니라 분 단위까지 정확히 계산
        """
        # 현재 시간을 분 단위로 문자열 변환
        now_str = now.strftime("%Y-%m-%d %H:%M")
        
        # ROUTINE_START, ROUTINE_END 조건을 minutes_before를 고려하여 계산
        # 루틴은 오늘 날짜 + 루틴 시간 - minutes_before = 현재 시간인 경우
        routine_start_condition = and_(
            models.Alert.type == "ROUTINE_START",
            func.to_char(
                func.cast(func.current_date(), DateTime) +
                func.cast(routine_models.Routine.start_time, Interval) -
                func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                "YYYY-MM-DD HH24:MI"
            ) == now_str
        )
        
        routine_end_condition = and_(
            models.Alert.type == "ROUTINE_END",
            func.to_char(
                func.cast(func.current_date(), DateTime) +
                func.cast(routine_models.Routine.end_time, Interval) -
                func.cast(func.concat(models.Alert.minutes_before, ' minutes'), Interval),
                "YYYY-MM-DD HH24:MI"
            ) == now_str
        )

        result = await db.execute(
            select(models.Alert)
            .join(models.Alert.routine)
            .options(
                joinedload(models.Alert.routine).joinedload(routine_models.Routine.user).joinedload(user_models.User.device_tokens),
            )
            .where(
                models.Alert.type.in_(["ROUTINE_START", "ROUTINE_END"]),
                or_(routine_start_condition, routine_end_condition)
            )
        )
        return result.scalars().unique().all()

alert_crud = AlertCRUD()
