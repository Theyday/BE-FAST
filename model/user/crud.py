from datetime import datetime

from typing import List, Optional

from sqlalchemy.orm import Session

from core.security import get_password_hash

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

# User

# Get User

# All(active/inactive) User


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.uid == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.username == username).first()

# Active User


def get_active_users(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.User]:
    return db.query(models.User).filter(models.User.is_active == True).offset(skip).limit(limit).all()


def get_active_user(db: Session, user_id: int) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.uid == user_id).filter(models.User.is_active == True).first()


def get_active_user_by_email(db: Session, email: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.email == email).filter(models.User.is_active == True).first()


def get_active_user_by_username(db: Session, username: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.username == username).filter(models.User.is_active == True).first()

# Inactive User


def get_inactive_users(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.User]:
    return db.query(models.User).filter(models.User.is_active == False).offset(skip).limit(limit).all()


def get_inactive_user(db: Session, user_id: int) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.uid == user_id).filter(models.User.is_active == False).first()


def get_inactive_user_by_email(db: Session, email: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.email == email).filter(models.User.is_active == False).first()


def get_inactive_user_by_username(db: Session, username: str) -> Optional[schemas.User]:
    return db.query(models.User).filter(models.User.username == username).filter(models.User.is_active == False).first()

# Create User


def create_user(db: Session, user: schemas.UserCreate) -> Optional[schemas.User]:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_active=user.is_active,
        is_admin=user.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Update User


def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    if db_user:
        db_user.username = user.username
        db_user.email = user.email
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Update User Password

def test_linux(db: Session, uid: int):
    db_user = db.query(models.User).filter(models.User.uid == uid).first()
    if db_user:
        db_user.deleted_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def get_linux(db:Session, uid:int):
    return db.query(models.User).filter(models.User.uid == uid).first().deleted_at


def update_user_password(db: Session, user_id: int, user: schemas.UserPasswordUpdate) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    if db_user:
        db_user.hashed_password = get_password_hash(user.password)
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Delete User


def delete_user(db: Session, user_id: int) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

# Activate User


def activate_user(db: Session, user_id: int) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).filter(
        models.User.is_active == False).first()
    if db_user:
        db_user.is_active = True
        db_user.updated_at = datetime.now()
        db_user.deleted_at = None
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Deactivate User


def deactivate_user(db: Session, user_id: int) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).filter(
        models.User.is_active == True).first()
    if db_user:
        db_user.is_active = False
        db_user.updated_at = datetime.now()
        db_user.deleted_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Promote User


def promote_user(db: Session, user_id: int) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).filter(
        models.User.is_admin == False).first()
    if db_user:
        db_user.is_admin = True
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Demote User


def demote_user(db: Session, user_id: int) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).filter(
        models.User.is_admin == True).first()
    if db_user:
        db_user.is_admin = False
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_user_info(db: Session, user_id: int, username: str, email: str) -> Optional[schemas.User]:
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    if db_user:
        db_user.username = username
        db_user.email = email
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

