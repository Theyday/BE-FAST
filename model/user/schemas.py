from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, validator



class UserBase(BaseModel):
    username: str = Field(..., max_length=255)
    email: EmailStr = Field(...)
    is_active: bool = Field(True)
    is_admin: bool = Field(False)
    
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str = Field(...)

    @validator('password')
    def password_length(cls, v) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @validator('email')
    def email_length(cls, v) -> str:
        if len(v) > 255:
            raise ValueError('Email must be less than 255 characters long')
        return v

    @validator('username')
    def username_length(cls, v) -> str:
        if len(v) > 255:
            raise ValueError('Username must be less than 255 characters long')
        return v


    @validator('is_active')
    def is_active_type(cls, v) -> bool:
        if type(v) is not bool:
            raise ValueError('is_active must be a boolean')
        return v

    @validator('is_admin')
    def is_admin_type(cls, v) -> bool:
        if type(v) is not bool:
            raise ValueError('is_admin must be a boolean')
        return v

    @validator('email')
    def email_lowercase(cls, v) -> str:
        return v.lower()


class UserUpdate(UserBase):
    pass

class UserPasswordUpdate(BaseModel):
    password: str = Field(...)

    @validator('password')
    def password_length(cls, v) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserInfoUpdate(BaseModel):
    uid: int
    username: str = Field(..., max_length=255)
    email: EmailStr = Field(...)
    
class User(UserBase):
    uid: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None

    class Config:
        orm_mode = True
