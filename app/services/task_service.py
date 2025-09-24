from datetime import date, datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from model.category.crud import category_crud
from model.database import get_async_session
from model.user.crud import user_crud
from model.schedule.task.crud import task_crud
from model.schedule.participant.crud import participant_crud
from model.schedule.alert.crud import alert_crud
from model.user import models as user_models
from model.category import models as category_models
from model.schedule.alert import models as alert_models
from model.schedule.event import models as event_models
from model.schedule.task import models as task_models
from model.schedule.participant import models as participant_models
from model.schedule.task import schemas as task_schemas
from model.schedule.alert.schemas import TaskAlertResponse
from model.category.schemas import CategoryResponse
from model.schedule.alert.alert_type import AlertType

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class TaskService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_async_session),
    ):
        self.db = db

    async def get_task_detail(self, task_id: int, current_user_id: int) -> task_schemas.TaskDetailResponse:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        task = await task_crud.get_task_by_id_with_category(self.db, task_id, user)
        if not task:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        participant = next((p for p in task.participants if p.user_id == user.id), None)
        if not participant:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        
        category_response = CategoryResponse(
            id=participant.category.id,
            name=participant.category.name,
            color=participant.category.color,
            isDefault=participant.category.is_default
        )

        alerts = await alert_crud.find_by_participant(self.db, participant)
        task_schedule_alert = next((a.minutes_before for a in alerts if a.type == AlertType.TASK_SCHEDULE), None)
        task_start_alert = next((a.minutes_before for a in alerts if a.type == AlertType.TASK_START), None)
        task_end_alert = next((a.minutes_before for a in alerts if a.type == AlertType.TASK_END), None)

        task_alert_response = TaskAlertResponse(
            taskSchedule=task_schedule_alert,
            taskStart=task_start_alert,
            taskEnd=task_end_alert
        )

        return task_schemas.TaskDetailResponse(
            id=task.id,
            type="TASK",
            name=task.name,
            description=task.description,
            location=task.location,
            startTime=task.start_time,
            endTime=task.end_time,
            scheduledTime=task.scheduled_time,
            isCompleted=task.is_completed,
            visibility=task.visibility,
            category=category_response,
            alert=task_alert_response,
            createdAt=task.created_at,
            completedAt=task.completed_at
        )

    async def edit_task(self, task_id: int, request: task_schemas.TaskEditRequest, current_user_id: int) -> None:
        task = await task_crud.get_task_by_id(self.db, task_id)
        if not task:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        # Update task fields
        if request.name is not None:
            task.name = request.name
        if request.location is not None:
            task.location = request.location
        if request.scheduled_time is not None:
            task.scheduled_time = request.scheduled_time
        if request.start_time is not None:
            task.start_time = request.start_time
        if request.end_time is not None:
            task.end_time = request.end_time
        if request.description is not None:
            task.description = request.description
        # 9/24 추가, 기존 수정에 할일 완료 토글을 합침 (기존의 완료 API는 구버전 앱을 위해 남겨둠)
        if request.is_completed is not None:
            if request.is_completed:
                task.is_completed = True
                # 내가 완료를 누른 날짜에 완료 처리
                task.completed_at = request.completed_at 
            else:
                task.is_completed = False
                task.completed_at = None

        await task_crud.save(self.db, task)

        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        participant = await participant_crud.find_by_task_and_participant(self.db, task, user)
        if not participant:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

        if request.category_id is not None:
            category = await category_crud.find_by_id_and_user(self.db, request.category_id, user)
            if not category:
                raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            participant.category = category
            await participant_crud.save(self.db, participant)

        if request.alert is not None:
            await alert_crud.delete_by_participant(self.db, participant)

            if request.alert and request.alert.task_schedule is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    participant_id=participant.id,
                    type=AlertType.TASK_SCHEDULE,
                    minutes_before=request.alert.task_schedule
                ))
            if request.alert and request.alert.task_start is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    participant_id=participant.id,
                    type=AlertType.TASK_START,
                    minutes_before=request.alert.task_start
                ))
            if request.alert and request.alert.task_end is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    participant_id=participant.id,
                    type=AlertType.TASK_END,
                    minutes_before=request.alert.task_end
                ))

    async def delete_task(self, task_id: int, current_user_id: int) -> None:
        task = await task_crud.get_task_by_id(self.db, task_id)
        if not task:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        is_owner = any(p.user_id == user.id and p.role == "OWNER" for p in task.participants)
        if not is_owner:
            raise CustomException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: User is not the owner of the task")

        # Deleting task will cascade delete participants and alerts if cascade is set in models.
        # If not, you need to manually delete participants and alerts first.
        await task_crud.delete(self.db, task)

    async def schedule_task(self, task_id: int, request: task_schemas.ScheduleTaskRequest, current_user_id: int) -> None:
        task = await task_crud.get_task_by_id(self.db, task_id)
        if not task:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        task.scheduled_time = request.scheduled_time
        await task_crud.save(self.db, task)

    async def toggle_task_complete(self, task_id: int, complete_date: date, current_user_id: int) -> None:
        task = await task_crud.get_task_by_id(self.db, task_id)
        if not task:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        if task.is_completed:
            task.completed_at = None
            task.is_completed = False
        else:
            task.completed_at = complete_date
            task.is_completed = True
        await task_crud.save(self.db, task)
