from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from ..database import Base
from ..base_time_model import BaseTimeModel

class User(BaseTimeModel):
    __tablename__ = "user_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    
    routines = relationship("Routine", back_populates="user")
    participants = relationship("Participant", back_populates="user")
    device_tokens = relationship("UserDeviceToken", back_populates="user")
    categories = relationship("Category", back_populates="user")
