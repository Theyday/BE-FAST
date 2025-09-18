from datetime import date, time, datetime
from typing import List, Union, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from model.database import get_db
from model.user.crud import user_crud
from model.schedule.event.crud import event_crud
from model.schedule.participant.crud import participant_crud
from model.schedule.alert.crud import alert_crud
from model.user import models as user_models
from model.category import models as category_models
from model.schedule.alert import models as alert_models
from model.schedule.event import models as event_models
from model.schedule.participant import models as participant_models
from model.schedule.event import schemas as event_schemas
from model.schedule.alert.schemas import EventAlertResponse
from model.category.schemas import CategoryResponse
from model.schedule.alert.alert_type import AlertType

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class EventService:
    def __init__(
        self, 
        db: Session = Depends(get_db),
    ):
        self.db = db

    def get_event_detail(self, event_id: int, username: str) -> event_schemas.EventDetailResponse:
        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        event = event_crud.get_event_by_id_with_category(self.db, event_id, user)
        if not event:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        
        participant = next((p for p in event.participants if p.user_id == user.id), None)
        if not participant:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        
        category_response = CategoryResponse(
            id=participant.category.id,
            name=participant.category.name,
            color=participant.category.color,
            isDefault=participant.category.is_default
        )

        alerts = alert_crud.find_by_participant(self.db, participant)
        event_start_alert = next((a.minutes_before for a in alerts if a.type == AlertType.EVENT_START), None)
        event_end_alert = next((a.minutes_before for a in alerts if a.type == AlertType.EVENT_END), None)

        event_alert_response = EventAlertResponse(
            eventStart=event_start_alert,
            eventEnd=event_end_alert
        )

        return event_schemas.EventDetailResponse(
            id=event.id,
            type="EVENT",
            name=event.name,
            description=event.description,
            location=event.location,
            startDate=event.start_date,
            endDate=event.end_date,
            startTime=event.start_time,
            endTime=event.end_time,
            visibility=event.visibility,
            category=category_response,
            alert=event_alert_response
        )

    def edit_event(self, event_id: int, request: event_schemas.EventEditRequest, username: str) -> None:
        event = event_crud.get_event_by_id(self.db, event_id)
        if not event:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        
        # Update event fields
        event.name = request.name
        event.location = request.location
        event.start_date = request.start_date
        event.end_date = request.end_date
        event.start_time = request.start_time
        event.end_time = request.end_time
        event.description = request.description
        event_crud.save(self.db, event) # Save event changes

        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        participant = participant_crud.find_by_event_and_participant(self.db, event, user)
        if not participant:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

        # Update category
        category = self.db.query(category_models.Category).filter(
            category_models.Category.id == request.category_id
        ).first()
        if not category:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        participant.category = category
        participant_crud.save(self.db, participant)

        # Update alerts
        alert_crud.delete_by_participant(self.db, participant)

        if request.alert and request.alert.event_start is not None:
            alert_crud.save(self.db, alert_models.Alert(
                participant_id=participant.id,
                type=AlertType.EVENT_START,
                minutes_before=request.alert.event_start
            ))
        if request.alert and request.alert.event_end is not None:
            alert_crud.save(self.db, alert_models.Alert(
                participant_id=participant.id,
                type=AlertType.EVENT_END,
                minutes_before=request.alert.event_end
            ))

    def delete_event(self, event_id: int, username: str) -> None:
        event = event_crud.get_event_by_id_with_category(self.db, event_id, user_models.User(id=username)) # Fetch with user context for owner check
        if not event:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        is_owner = any(p.user_id == user.id and p.role == "OWNER" for p in event.participants)
        if not is_owner:
            raise CustomException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: User is not the owner of the event")

        # Deleting event will cascade delete participants and alerts if cascade is set in models.
        # If not, you need to manually delete participants and alerts first.
        event_crud.delete(self.db, event)
