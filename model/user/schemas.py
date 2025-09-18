from typing import Optional
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    image: Optional[str] = None

class UserCreate(BaseModel):
    phone_or_email: str 
    name: str

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True

class SignUpRequest(BaseModel):
    phone_or_email: str = Field(..., alias="phoneOrEmail")
    name: str

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str

class DeviceTokenRequest(BaseModel):
    token: str
