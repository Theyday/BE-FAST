from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field

from ...category.schemas import CategoryResponse
from ...schedule.visibility import Visibility
from ..alert.schemas import TaskAlertResponse

class TaskResponse(BaseModel):
    id: int
    type: str = "TASK"
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    scheduled_time: Optional[datetime] = Field(None, alias="scheduledTime")
    is_completed: bool = Field(False, alias="isCompleted")
    color: str

    class Config:
        from_attributes = True
        populate_by_name = True

class TaskDetailResponse(BaseModel):
    id: int
    type: str = "TASK"
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    scheduled_time: Optional[datetime] = Field(None, alias="scheduledTime")
    is_completed: bool = Field(False, alias="isCompleted")
    visibility: Visibility
    category: CategoryResponse
    alert: Optional[TaskAlertResponse] = None
    created_at: datetime = Field(..., alias="createdAt")
    completed_at: datetime = Field(..., alias="completedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

class ScheduleTaskRequest(BaseModel):
    scheduled_time: Optional[datetime] = Field(None, alias="scheduledTime")

    class Config:
        from_attributes = True
        populate_by_name = True

class TaskEditRequest(BaseModel):
    name: str
    location: Optional[str] = None
    scheduled_time: Optional[datetime] = Field(None, alias="scheduledTime")
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    description: Optional[str] = None
    category_id: int = Field(..., alias="categoryId")
    alert: Optional[TaskAlertResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True
