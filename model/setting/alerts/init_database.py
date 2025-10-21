import json

import os

from typing import Annotated

from fastapi import Depends

from sqlalchemy.orm import Session

from core.config import settings
from model.database import AsyncSessionLocal, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import engine
from .crud import alert_crud
from . import schemas
from model.user.crud import UserCRUD

# 모든 모델을 import하여 Base.metadata에 등록
from model.user.models import User
from .models import UserAlert

async def init_database(engine: engine):
    # Create Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check User with Alert Settings
    async with AsyncSessionLocal() as db:
        user_crud = UserCRUD()  # 인스턴스 생성
        users = await user_crud.get_all_users(db)
        for user in users:
            alert_settings = await alert_crud.get_alert_setting_by_user_id(db, user.id)
            if not alert_settings:
                await alert_crud.create_default_alert_setting(db, user.id)
    