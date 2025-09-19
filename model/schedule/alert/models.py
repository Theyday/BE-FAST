from sqlalchemy import Column, BigInteger, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from .alert_type import AlertType
from ...base_time_model import BaseTimeModel

class Alert(BaseTimeModel):
    __tablename__ = "alert_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    participant_id = Column(BigInteger, ForeignKey("participant_tb.id"), nullable=True)
    routine_id = Column(BigInteger, ForeignKey("routine_tb.id"), nullable=True)
    type = Column(Enum(AlertType), nullable=False)
    minutes_before = Column(Integer, nullable=False)

    participant = relationship("Participant", back_populates="alerts")
    routine = relationship("Routine", back_populates="alerts")
