from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Date, Enum
from sqlalchemy.orm import relationship

from ..visibility import Visibility
from ...base_time_model import BaseTimeModel

class Task(BaseTimeModel):
    __tablename__ = "task_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, nullable=False)
    completed_at = Column(Date, nullable=True)
    source_text = Column(String(500), nullable=True)
    visibility = Column(String(20), nullable=False)

    participants = relationship("Participant", back_populates="task")
