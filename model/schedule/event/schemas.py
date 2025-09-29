from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field

from ...category.schemas import CategoryResponse
from ...schedule.visibility import Visibility
from ..alert.schemas import EventAlertResponse

class EventResponse(BaseModel):
    id: int
    type: str = "EVENT"
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    visibility: Visibility
    color: str

    class Config:
        from_attributes = True
        populate_by_name = True

class EventCreateRequest(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    description: Optional[str] = None
    visibility: Visibility
    category_id: int = Field(..., alias="categoryId")
    alert: Optional[EventAlertResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class EventDetailResponse(BaseModel):
    id: int
    type: str = "EVENT"
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    visibility: Visibility
    category: CategoryResponse
    alert: Optional[EventAlertResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class EventEditRequest(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    description: Optional[str] = None
    category_id: int = Field(..., alias="categoryId")
    alert: Optional[EventAlertResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True
