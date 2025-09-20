import httpx
from enum import Enum
from typing import Dict, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from model.schedule.alert.crud import alert_crud
from model.schedule.alert.alert_type import AlertType
from model.database import get_async_session

class NotificationType(str, Enum):
    SCHEDULE_REMINDER = "SCHEDULE_REMINDER"

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

# APScheduler 인스턴스 생성
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

async def send_push(
    type: NotificationType,
    to: str,
    title: str,
    body: str,
    data: Dict[str, Any]
):
    headers = {
        "host": "exp.host",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
    }

    data["type"] = type.name

    payload = {
        "to": to,
        "title": title,
        "body": body,
        "data": data,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(EXPO_PUSH_URL, json=payload, headers=headers)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
        except httpx.HTTPStatusError as e:
            pass
        except Exception as e:
            pass

async def schedule_alerts():
    """매분마다 실행되는 스케줄링 함수"""
    now = datetime.now()
    
    # 데이터베이스 세션 가져오기
    async for db in get_async_session():
        try:
            # 각 타입별로 알림 조회
            event_alerts = await alert_crud.find_event_alerts_to_send(db, now)
            task_alerts = await alert_crud.find_task_alerts_to_send(db, now)
            routine_alerts = await alert_crud.find_routine_alerts_to_send(db, now)
            
            # 루틴 알림 필터링 (요일 체크)
            # Java 코드와 동일한 로직: now.getDayOfWeek().getValue() % 7
            filtered_routine_alerts = []
            for alert in routine_alerts:
                if alert.routine and alert.routine.days_of_week:
                    day_of_week = (now.weekday() + 1) % 7
                    if str(day_of_week) in alert.routine.days_of_week:
                        filtered_routine_alerts.append(alert)
            
            # 모든 알림 합치기
            all_alerts = event_alerts + task_alerts + filtered_routine_alerts
            
            # 각 알림에 대해 푸시 알림 전송
            for alert in all_alerts:
                user = alert.participant.user if alert.participant else alert.routine.user
                if not user:
                    continue
                    
                title = get_alert_title(alert)
                when = get_when(alert.minutes_before)
                alert_type = get_alert_type(alert.type)
                time_str = get_time(alert, now)
                body = f"{when} {alert_type} | {time_str}"
                
                # 사용자의 모든 디바이스 토큰에 알림 전송
                for device_token in user.device_tokens:
                    await send_push(
                        NotificationType.SCHEDULE_REMINDER,
                        device_token.token,
                        title,
                        body,
                        {}
                    )
                    
        except Exception as e:
            pass
        finally:
            await db.aclose()
        break  # 한 번만 실행하고 종료

def get_alert_title(alert) -> str:
    """알림 제목 생성"""
    if alert.participant:
        if alert.participant.event:
            return alert.participant.event.name
        elif alert.participant.task:
            return alert.participant.task.name
    elif alert.routine:
        return alert.routine.name
    return "알림"

def get_when(minutes_before: int) -> str:
    """분 단위를 한국어로 변환"""
    when_map = {
        0: "지금",
        5: "5분 후",
        10: "10분 후",
        15: "15분 후",
        30: "30분 후",
        60: "1시간 후",
        120: "2시간 후",
        720: "12시간 후",
        1440: "1일 후",
        2880: "2일 후",
        10080: "1주일 후"
    }
    return when_map.get(minutes_before, "")

def get_alert_type(alert_type: AlertType) -> str:
    """알림 타입을 한국어로 변환"""
    type_map = {
        AlertType.EVENT_START: "일정 시작",
        AlertType.EVENT_END: "일정 종료",
        AlertType.TASK_SCHEDULE: "할일 시작",
        AlertType.TASK_START: "할일 기한 시작",
        AlertType.TASK_END: "할일 기한 종료",
        AlertType.ROUTINE_START: "루틴 시작",
        AlertType.ROUTINE_END: "루틴 종료"
    }
    return type_map.get(alert_type, "")

def get_time(alert, now: datetime) -> str:
    """알림 시간을 한국어 형식으로 변환"""
    hour = 0
    minute = 0
    
    if alert.type == AlertType.EVENT_START:
        if alert.participant and alert.participant.event and alert.participant.event.start_time:
            hour = alert.participant.event.start_time.hour
            minute = alert.participant.event.start_time.minute
    elif alert.type == AlertType.EVENT_END:
        if alert.participant and alert.participant.event and alert.participant.event.end_time:
            hour = alert.participant.event.end_time.hour
            minute = alert.participant.event.end_time.minute
    elif alert.type == AlertType.TASK_SCHEDULE:
        if alert.participant and alert.participant.task and alert.participant.task.scheduled_time:
            hour = alert.participant.task.scheduled_time.hour
            minute = alert.participant.task.scheduled_time.minute
    elif alert.type == AlertType.TASK_START:
        if alert.participant and alert.participant.task and alert.participant.task.start_time:
            hour = alert.participant.task.start_time.hour
            minute = alert.participant.task.start_time.minute
    elif alert.type == AlertType.TASK_END:
        if alert.participant and alert.participant.task and alert.participant.task.end_time:
            hour = alert.participant.task.end_time.hour
            minute = alert.participant.task.end_time.minute
    elif alert.type == AlertType.ROUTINE_START:
        if alert.routine and alert.routine.start_time:
            hour = alert.routine.start_time.hour
            minute = alert.routine.start_time.minute
    elif alert.type == AlertType.ROUTINE_END:
        if alert.routine and alert.routine.end_time:
            hour = alert.routine.end_time.hour
            minute = alert.routine.end_time.minute
    
    ampm = "오전" if hour < 12 else "오후"
    hour12 = 12 if hour % 12 == 0 else hour % 12
    
    return f"{ampm} {hour12}:{minute:02d}"

def start_scheduler():
    """스케줄러 시작"""
    # 매분마다 schedule_alerts 함수 실행
    scheduler.add_job(
        schedule_alerts,
        CronTrigger(second=0, timezone="Asia/Seoul"),  # 매분 0초에 실행
        id="schedule_alerts",
        replace_existing=True
    )
    scheduler.start()
    print("Notification scheduler started")

def stop_scheduler():
    """스케줄러 중지"""
    scheduler.shutdown()
    print("Notification scheduler stopped")
