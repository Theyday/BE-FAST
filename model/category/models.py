from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..base_time_model import BaseTimeModel

class Category(BaseTimeModel):
    __tablename__ = "category_tb"

    id = Column(BigInteger, primary_key=True, index=True)
    is_default = Column(Boolean, nullable=False)
    name = Column(String(20), nullable=False)
    color = Column(String(20), nullable=False)
    user_id = Column(BigInteger, ForeignKey("user_tb.id"), nullable=False)

    user = relationship("User", back_populates="categories")
    participants = relationship("Participant", back_populates="category")
