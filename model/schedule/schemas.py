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

class OperationLog(BaseModel):
    table_name: str = Field(..., alias="tableName", description="수정 대상 테이블명: events, tasks, routines 중 하나")
    row_id: int = Field(..., alias="rowId", description="해당 모델의 ID")
    operation: str = Field(..., description="create, update, delete 중 하나")
    payload: Optional[dict] = Field(None, description="수정/생성 요청 바디, 삭제라면 없음")
    timestamp: int = Field(..., description="오프라인에서 해당 수정이 이루어진 시간 (UNIX timestamp)")

    class Config:
        from_attributes = True
        populate_by_name = True

class ScheduleBatchRequest(BaseModel):
    operations: List[OperationLog]

    class Config:
        from_attributes = True
        populate_by_name = True