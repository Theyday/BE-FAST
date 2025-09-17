from datetime import time
from typing import Optional, List
from pydantic import BaseModel, Field

from ..alert.schemas import RoutineAlertResponse

class RoutineBase(BaseModel):
    name: str
    days_of_week: str = Field(..., alias="daysOfWeek")
    start_time: time = Field(..., alias="startTime")
    end_time: time = Field(..., alias="endTime")
    icon: str
    color: str

    class Config:
        from_attributes = True
        populate_by_name = True

class RoutineCreateRequest(RoutineBase):
    alert: Optional[RoutineAlertResponse] = None

class RoutineResponse(RoutineBase):
    id: int
    alert: Optional[RoutineAlertResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True
