from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from ...database import Base

class UserDeviceToken(Base):
    __tablename__ = "user_device_token_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user_tb.id"), nullable=True)
    token = Column(String, nullable=False)

    user = relationship("User", back_populates="device_tokens")
