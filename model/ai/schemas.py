from datetime import date, time, datetime
from typing import Optional, Union
from pydantic import BaseModel, Field


class CreateFromTextRequest(BaseModel):
    text: str


class CategoryInfo(BaseModel):
    id: int
    name: str


class AIEventResponse(BaseModel):
    id: Optional[int] = None
    type: str
    name: str
    location: Optional[str] = None
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate") 
    start_time: Optional[time] = Field(None, alias="startTime")
    end_time: Optional[time] = Field(None, alias="endTime")
    visibility: str = "PRIVATE"
    source_text: Optional[str] = Field(None, alias="sourceText")
    color: str

    class Config:
        from_attributes = True
        populate_by_name = True


class AITaskResponse(BaseModel):
    id: Optional[int] = None
    type: str
    name: str
    location: Optional[str] = None
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    scheduled_time: Optional[datetime] = Field(None, alias="scheduledTime")
    is_completed: bool = Field(False, alias="isCompleted")
    visibility: str = "PRIVATE"
    source_text: Optional[str] = Field(None, alias="sourceText")
    color: str

    class Config:
        from_attributes = True
        populate_by_name = True


# Union type for AI response
AIResponse = Union[AIEventResponse, AITaskResponse]
