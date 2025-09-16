from datetime import datetime

from typing import List, Optional

from sqlalchemy.orm import Session

from core.security import get_password_hash

from . import models, schemas

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

