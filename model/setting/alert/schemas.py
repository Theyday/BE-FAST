from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    user_id: int
    event_start: int
    task_end: int
    routine_start: int

class AlertCreate(AlertBase):
    pass

class AlertUpdate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True