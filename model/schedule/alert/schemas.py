from typing import Optional
from pydantic import BaseModel, Field

class EventAlertResponse(BaseModel):
    event_start: Optional[int] = Field(None, alias="eventStart")
    event_end: Optional[int] = Field(None, alias="eventEnd")

    class Config:
        from_attributes = True
        populate_by_name = True

class TaskAlertResponse(BaseModel):
    task_schedule: Optional[int] = Field(None, alias="taskSchedule")
    task_start: Optional[int] = Field(None, alias="taskStart")
    task_end: Optional[int] = Field(None, alias="taskEnd")

    class Config:
        from_attributes = True
        populate_by_name = True

class RoutineAlertResponse(BaseModel):
    routine_start: Optional[int] = Field(None, alias="routineStart")
    routine_end: Optional[int] = Field(None, alias="routineEnd")

    class Config:
        from_attributes = True
        populate_by_name = True
