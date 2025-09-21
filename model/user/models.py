from sqlalchemy import Column, BigInteger, Identity, String
from sqlalchemy.orm import relationship

from ..base_time_model import BaseTimeModel

class User(BaseTimeModel):
    __tablename__ = "user_tb"

    id = Column(BigInteger, Identity(start=1, increment=1), primary_key=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    
    routines = relationship("Routine", back_populates="user")
    participants = relationship("Participant", back_populates="user")
    device_tokens = relationship("UserDeviceToken", back_populates="user")
    categories = relationship("Category", back_populates="user")
