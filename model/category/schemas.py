from typing import Optional
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    color: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    is_default: bool

    class Config:
        from_attributes = True

class CategoryResponseWithoutName(BaseModel):
    id: int
    color: str
    is_default: bool

    class Config:
        from_attributes = True
