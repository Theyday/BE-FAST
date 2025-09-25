from sqlalchemy import Column, BigInteger, String, Date, Time, Enum
from sqlalchemy.orm import relationship

from ...base_time_model import BaseTimeModel

class Event(BaseTimeModel):
    __tablename__ = "event_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    source_text = Column(String(500), nullable=True)
    visibility = Column(String(20), nullable=False)
    participants = relationship("Participant", back_populates="event", cascade="all, delete-orphan")
