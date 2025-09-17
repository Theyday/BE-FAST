from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ScheduleType(str, Enum):
    EVENT = "EVENT"
    TASK = "TASK"

class CalendarItemDto(BaseModel):
    id: int
    type: str
    name: str
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    color: str
    is_completed: bool = Field(False, alias="isCompleted")
    is_scheduled: bool = Field(False, alias="isScheduled")

    class Config:
        from_attributes = True
        populate_by_name = True
