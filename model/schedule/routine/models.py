from sqlalchemy import Column, BigInteger, String, ForeignKey, Time
from sqlalchemy.orm import relationship

from ...base_time_model import BaseTimeModel

class Routine(BaseTimeModel):
    __tablename__ = "routine_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user_tb.id"), nullable=False)
    name = Column(String(20), nullable=False)
    days_of_week = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    icon = Column(String(50), nullable=False)
    color = Column(String(10), nullable=False)

    user = relationship("User", back_populates="routines")
    alerts = relationship("Alert", back_populates="routine")
