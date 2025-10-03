from datetime import datetime

from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from ..user.deviceToken import models as device_token_models

class UserCRUD:
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    async def get_user_by_phone(self, db: AsyncSession, phone: str) -> Optional[models.User]:
        result = await db.execute(select(models.User).filter(models.User.phone == phone))
        return result.scalars().first()

    async def get_user_by_email_or_phone(self, db: AsyncSession, value: str) -> Optional[models.User]:
        result = await db.execute(
            select(models.User).filter((models.User.email == value) | (models.User.phone == value))
        )
        return result.scalars().first()

    async def exists_by_email(self, db: AsyncSession, email: str) -> bool:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first() is not None

    async def exists_by_phone(self, db: AsyncSession, phone: str) -> bool:
        result = await db.execute(select(models.User).filter(models.User.phone == phone))
        return result.scalars().first() is not None

    async def create_user(self, db: AsyncSession, user_create: schemas.UserCreate) -> models.User:
        db_user = models.User(
            name=user_create.name,
            email=user_create.phone_or_email if "@" in user_create.phone_or_email else None,
            phone=user_create.phone_or_email if "@" not in user_create.phone_or_email else None,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    async def save_user(self, db: AsyncSession, user: models.User) -> models.User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

class UserDeviceTokenCRUD:
    async def find_by_token(self, db: AsyncSession, token: str) -> Optional[device_token_models.UserDeviceToken]:
        result = await db.execute(select(device_token_models.UserDeviceToken).filter(device_token_models.UserDeviceToken.token == token))
        return result.scalars().first()

    async def save_device_token(self, db: AsyncSession, device_token: device_token_models.UserDeviceToken) -> device_token_models.UserDeviceToken:
        db.add(device_token)
        await db.commit()
        await db.refresh(device_token)
        return device_token
    
    async def delete_by_token(self, db: AsyncSession, token: str) -> None:
        await db.execute(delete(device_token_models.UserDeviceToken).filter(
            device_token_models.UserDeviceToken.token == token
        ))
        await db.commit()

user_crud = UserCRUD()
user_device_token_crud = UserDeviceTokenCRUD()
