from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from model.database import get_async_session
from model.user.crud import user_crud
from model.schedule.routine.crud import routine_crud
from model.schedule.alert.crud import alert_crud
from model.user import models as user_models
from model.schedule.alert import models as alert_models
from model.schedule.routine import models as routine_models
from model.schedule.routine import schemas as routine_schemas
from model.schedule.alert.schemas import RoutineAlertResponse
from model.schedule.alert.alert_type import AlertType

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class RoutineService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_async_session),
    ):
        self.db = db

    async def create_routine(self, request: routine_schemas.RoutineCreateRequest, current_user_id: int) -> None:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        new_routine = routine_models.Routine(
            user_id=user.id,
            name=request.name,
            days_of_week=request.days_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            icon=request.icon,
            color=request.color
        )
        await routine_crud.save(self.db, new_routine)

        if request.alert:
            if request.alert.routine_start is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    routine_id=new_routine.id,
                    type=AlertType.ROUTINE_START,
                    minutes_before=request.alert.routine_start
                ))
            if request.alert.routine_end is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    routine_id=new_routine.id,
                    type=AlertType.ROUTINE_END,
                    minutes_before=request.alert.routine_end
                ))

    async def update_routine(self, routine_id: int, request: routine_schemas.RoutineCreateRequest, current_user_id: int) -> None:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        routine = await routine_crud.get_routine_by_id(self.db, routine_id)
        if not routine:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Routine not found")

        if not routine.user_id == user.id:
            raise CustomException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: User is not the owner of the routine")
        
        routine.name = request.name
        routine.days_of_week = request.days_of_week
        routine.start_time = request.start_time
        routine.end_time = request.end_time
        routine.icon = request.icon
        routine.color = request.color
        await routine_crud.save(self.db, routine)

        await alert_crud.delete_by_routine(self.db, routine)

        if request.alert:
            if request.alert.routine_start is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    routine_id=routine.id,
                    type=AlertType.ROUTINE_START,
                    minutes_before=request.alert.routine_start
                ))
            if request.alert.routine_end is not None:
                await alert_crud.save(self.db, alert_models.Alert(
                    routine_id=routine.id,
                    type=AlertType.ROUTINE_END,
                    minutes_before=request.alert.routine_end
                ))

    async def get_my_routines(self, current_user_id: int) -> List[routine_schemas.RoutineResponse]:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        routines = await routine_crud.find_by_user_with_alerts(self.db, user)

        

        response_routines = []
        for routine in routines:
            routine_start_alert = next((a.minutes_before for a in routine.alerts if a.type == AlertType.ROUTINE_START), None)
            routine_end_alert = next((a.minutes_before for a in routine.alerts if a.type == AlertType.ROUTINE_END), None)
            alert_response = RoutineAlertResponse(
                routineStart=routine_start_alert,
                routineEnd=routine_end_alert
            )
            response_routines.append(routine_schemas.RoutineResponse(
                id=routine.id,
                name=routine.name,
                daysOfWeek=routine.days_of_week,
                startTime=routine.start_time,
                endTime=routine.end_time,
                icon=routine.icon,
                color=routine.color,
                alert=alert_response
            ))
        return response_routines

    async def get_routine(self, routine_id: int, current_user_id: int) -> routine_schemas.RoutineResponse:
        routine = await routine_crud.get_routine_by_id(self.db, routine_id)
        if not routine:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Routine not found")
        
        routine_start_alert = next((a.minutes_before for a in routine.alerts if a.type == AlertType.ROUTINE_START), None)
        routine_end_alert = next((a.minutes_before for a in routine.alerts if a.type == AlertType.ROUTINE_END), None)

        alert_response = RoutineAlertResponse(
            routineStart=routine_start_alert,
            routineEnd=routine_end_alert
        )

        return routine_schemas.RoutineResponse(
            id=routine.id,
            name=routine.name,
            daysOfWeek=routine.days_of_week,
            startTime=routine.start_time,
            endTime=routine.end_time,
            icon=routine.icon,
            color=routine.color,
            alert=alert_response
        )

    async def delete_routine(self, routine_id: int, current_user_id: int) -> None:
        user = await user_crud.get_user_by_id(self.db, current_user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        routine = await routine_crud.get_routine_by_id(self.db, routine_id)
        if not routine:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Routine not found")

        if not routine.user_id == user.id:
            raise CustomException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: User is not the owner of the routine")
        
        await routine_crud.delete(self.db, routine)

    # This method is called from UserService during user creation
    async def create_default_routines_for_user(self, db: AsyncSession, user: user_models.User) -> List[routine_models.Routine]:
        # Use the CRUD method directly, as it handles the creation logic
        return await routine_crud.create_default_routines_for_user(db, user)
