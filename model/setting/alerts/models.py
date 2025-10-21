from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, DateTime, Date, Enum
from sqlalchemy.orm import relationship

from model.base_time_model import BaseTimeModel

class UserAlert(BaseTimeModel):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user_tb.id"), nullable=False)
    event_start = Column(BigInteger, default=False)
    task_end = Column(BigInteger, default=False)
    routine_start = Column(BigInteger, default=False)

    user = relationship("User", back_populates="alerts")