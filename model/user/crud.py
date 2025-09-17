from datetime import datetime

from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas
from ..user.deviceToken import models as device_token_models

class UserCRUD:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    def get_user_by_phone(self, db: Session, phone: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.phone == phone).first()

    def get_user_by_email_or_phone(self, db: Session, value: str) -> Optional[models.User]:
        return db.query(models.User).filter(
            (models.User.email == value) | (models.User.phone == value)
        ).first()

    def exists_by_email(self, db: Session, email: str) -> bool:
        return db.query(models.User).filter(models.User.email == email).first() is not None

    def exists_by_phone(self, db: Session, phone: str) -> bool:
        return db.query(models.User).filter(models.User.phone == phone).first() is not None

    def create_user(self, db: Session, user_create: schemas.UserCreate) -> models.User:
        db_user = models.User(
            name=user_create.name,
            email=user_create.phone_or_email if "@" in user_create.phone_or_email else None,
            phone=user_create.phone_or_email if "@" not in user_create.phone_or_email else None,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def save_user(self, db: Session, user: models.User) -> models.User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class UserDeviceTokenCRUD:
    def find_by_token(self, db: Session, token: str) -> Optional[device_token_models.UserDeviceToken]:
        return db.query(device_token_models.UserDeviceToken).filter(device_token_models.UserDeviceToken.token == token).first()

    def save_device_token(self, db: Session, device_token: device_token_models.UserDeviceToken) -> device_token_models.UserDeviceToken:
        db.add(device_token)
        db.commit()
        db.refresh(device_token)
        return device_token
    
    def delete_by_token(self, db: Session, token: str) -> None:
        db.query(device_token_models.UserDeviceToken).filter(device_token_models.UserDeviceToken.token == token).delete()
        db.commit()

user_crud = UserCRUD()
user_device_token_crud = UserDeviceTokenCRUD()
