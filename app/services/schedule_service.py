from datetime import date, datetime, time
from typing import List, Union, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from model.database import get_db
from model.user.crud import user_crud
from model.schedule.event.crud import event_crud
from model.schedule.task.crud import task_crud
from model.schedule.participant.crud import participant_crud
from model.user import models as user_models
from model.schedule.event import models as event_models
from model.schedule.task import models as task_models
from model.schedule.participant import models as participant_models
from model.schedule import schemas as schedule_schemas
from model.schedule.schemas import CalendarItemDto, ScheduleType
from model.schedule.visibility import Visibility

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ScheduleService:
    def __init__(
        self, 
        db: Session = Depends(get_db),
    ):
        self.db = db

    def get_calendar_items_by_range(self, start_date: date, end_date: date, username: str) -> List[CalendarItemDto]:
        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        items = []
        # Fetch events
        events = event_crud.find_by_participant_and_range(self.db, user, start_date, end_date)
        for event in events:
            color = "#CCCCCC"  # 기본값
            for participant in event.participants:
                if participant.user_id == user.id and participant.category:
                    color = participant.category.color
                    break

            items.append(CalendarItemDto(
                id=event.id,
                type=ScheduleType.EVENT.value,
                name=event.name,
                startDate=event.start_date,
                endDate=event.end_date,
                startTime=event.start_time,
                endTime=event.end_time,
                color=color,
                isCompleted=False, # Events are not completed
                isScheduled=event.start_time is not None or event.end_time is not None # If there's any time, it's scheduled
            ))
        
        uncompleted_tasks = task_crud.find_uncompleted_tasks_by_participant_and_range(self.db, user, start_date, end_date)
        for task in uncompleted_tasks:
            color = "#CCCCCC"
            for participant in task.participants:
                if participant.user_id == user.id and participant.category:
                    color = participant.category.color
                    break
            items.append(CalendarItemDto(
                id=task.id,
                type=ScheduleType.TASK.value,
                name=task.name,
                startDate=task.start_time.date() if task.start_time else None,
                endDate=task.end_time.date() if task.end_time else None,
                startTime=task.start_time.time() if task.start_time else None,
                endTime=task.end_time.time() if task.end_time else None,
                color=color,
                isCompleted=task.is_completed,
                isScheduled=task.scheduled_time is not None
            ))

        # Fetch completed tasks
        completed_tasks = task_crud.find_completed_tasks_by_participant_and_range(self.db, user, start_date, end_date)
        for task in completed_tasks:
            color = "#CCCCCC" # Placeholder color
            if task.participants and task.participants[0].category:
                color = task.participants[0].category.color
            items.append(CalendarItemDto(
                id=task.id,
                type=ScheduleType.TASK.value,
                name=task.name,
                start_date=task.completed_at,
                end_date=task.completed_at,
                start_time=None,
                end_time=None,
                color=color,
                is_completed=task.is_completed,
                is_scheduled=False # Completed tasks might not have scheduled time in this context
            ))
        
        return items

    @staticmethod
    def _get_category_color_from_participant(participant: participant_models.Participant) -> str:
        if participant and participant.category: # Assuming category is loaded
            return participant.category.color
        return "#000000" # Default color if not found

    def change_schedule_type(self, schedule_id: int, current_type: ScheduleType, username: str) -> Union[dict, None]:
        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if current_type == ScheduleType.EVENT: # Event -> Task
            event = event_crud.get_event_by_id(self.db, schedule_id)
            if not event:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
            
            participant = participant_crud.find_by_event_and_participant(self.db, event, user)
            if not participant:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
            
            task_scheduled_time: Optional[datetime] = None
            task_start_time: Optional[datetime] = None
            task_end_time: Optional[datetime] = None

            if event.start_time and (not event.end_time):
                task_scheduled_time = datetime.combine(event.start_date, event.start_time)
            elif event.start_time and event.end_time:
                task_start_time = datetime.combine(event.start_date, event.start_time)
                task_end_time = datetime.combine(event.end_date, event.end_time)
            else:
                task_start_time = datetime.combine(event.start_date, time.min) # Start of day
                task_end_time = datetime.combine(event.end_date, time(23, 59, 59)) # End of day

            new_task = task_models.Task(
                name=event.name,
                description=event.description,
                location=event.location,
                scheduled_time=task_scheduled_time,
                start_time=task_start_time,
                end_time=task_end_time,
                is_completed=False,
                source_text=event.source_text,
                visibility=event.visibility
            )
            task_crud.save(self.db, new_task)

            participant.event = None
            participant.task = new_task
            # participant.category remains the same
            participant_crud.save(self.db, participant)

            event_crud.delete(self.db, event)

            # Return TaskDto.TaskResponse.of(task, participant.getCategory().getColor());
            # This requires a new TaskResponse schema and a way to get category color
            color = self._get_category_color_from_participant(participant) # Assuming category is loaded with participant
            return {"id": new_task.id, "type": ScheduleType.TASK.value, "name": new_task.name, "color": color}

        elif current_type == ScheduleType.TASK: # Task -> Event
            task = task_crud.get_task_by_id(self.db, schedule_id)
            if not task:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
            
            participant = participant_crud.find_by_task_and_participant(self.db, task, user)
            if not participant:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
            
            event_start_date: Optional[date] = None
            event_end_date: Optional[date] = None
            event_start_time: Optional[time] = None
            event_end_time: Optional[time] = None

            if task.scheduled_time:
                event_start_date = task.scheduled_time.date()
                event_end_date = task.scheduled_time.date()
                event_start_time = task.scheduled_time.time()
                event_end_time = None
            elif task.start_time and task.end_time:
                event_start_date = task.start_time.date()
                event_end_date = task.end_time.date()
                event_start_time = task.start_time.time()
                event_end_time = task.end_time.time()
            elif task.start_time:
                event_start_date = task.start_time.date()
                event_end_date = task.start_time.date()
                event_start_time = None
                event_end_time = None
            elif task.end_time:
                event_start_date = task.end_time.date()
                event_end_date = task.end_time.date()
                event_start_time = None
                event_end_time = None
            else:
                today = date.today()
                event_start_date = today
                event_end_date = today
                event_start_time = None
                event_end_time = None

            new_event = event_models.Event(
                name=task.name,
                description=task.description,
                location=task.location,
                start_date=event_start_date,
                end_date=event_end_date,
                start_time=event_start_time,
                end_time=event_end_time,
                source_text=task.source_text,
                visibility=task.visibility
            )
            event_crud.save(self.db, new_event)

            participant.event = new_event
            participant.task = None
            # participant.category remains the same
            participant_crud.save(self.db, participant)

            task_crud.delete(self.db, task)

            # Return EventDto.EventResponse.of(event, participant.getCategory().getColor());
            # This requires a new EventResponse schema and a way to get category color
            color = self._get_category_color_from_participant(participant) # Assuming category is loaded with participant
            return {"id": new_event.id, "type": ScheduleType.EVENT.value, "name": new_event.name, "color": color}

        return None
