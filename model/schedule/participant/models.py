from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from ...base_time_model import BaseTimeModel

class Participant(BaseTimeModel):
    __tablename__ = "participant_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user_tb.id"), nullable=False)
    event_id = Column(BigInteger, ForeignKey("event_tb.id"), nullable=True)
    task_id = Column(BigInteger, ForeignKey("task_tb.id"), nullable=True)
    category_id = Column(BigInteger, ForeignKey("category_tb.id"), nullable=False)
    status = Column(String, nullable=False)
    role = Column(String, nullable=False)

    user = relationship("User", back_populates="participants")
    event = relationship("Event", back_populates="participants")
    task = relationship("Task", back_populates="participants")
    category = relationship("Category", back_populates="participants")
    alerts = relationship("Alert", back_populates="participant", cascade="all, delete-orphan")
