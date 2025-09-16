from datetime import datetime

from sqlalchemy import Column, BigInteger,  String, Boolean, DateTime
from sqlalchemy.orm import relationship

from model.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
