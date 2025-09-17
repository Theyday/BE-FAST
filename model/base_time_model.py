from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import declarative_base

@as_declarative()
class Base:
    """Base class which provides automated table name
    and ensures that all models inherit from this base for ORM to function correctly.
    """
    @declared_attr
    def __tablename__(cls) -> str:
        # Generate __tablename__ from class name, e.g., 'User' -> 'user_tb'
        # Assuming your tables are suffixed with _tb as per your Spring Boot example
        return cls.__name__.lower() + "_tb"

    id: any # To suppress mypy error for missing id column in Base

Base = declarative_base(cls=Base)

class BaseTimeModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
