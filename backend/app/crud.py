from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
from typing import Dict, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_phone(db: Session, phone: str):
    """根据手机号获取用户"""
    return db.query(models.User).filter(models.User.phone == phone).first()


def get_user_by_username_or_phone(db: Session, username_or_phone: str):
    """根据用户名或手机号获取用户"""
    return db.query(models.User).filter(
        or_(
            models.User.username == username_or_phone,
            models.User.phone == username_or_phone
        )
    ).first()


def create_user(db: Session, user: schemas.UserCreate):
    """创建用户"""
    # 检查用户名是否已存在
    if get_user_by_username(db, user.username):
        raise ValueError("用户名已存在")
    
    # 验证并处理手机号
    if not user.phone:
        raise ValueError("手机号不能为空")
    
    phone = str(user.phone).strip()
    if not phone:
        raise ValueError("手机号不能为空")
    
    # 检查手机号是否已被注册
    existing_user = db.query(models.User).filter(models.User.phone == phone).first()
    if existing_user:
        raise ValueError("手机号已被注册")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        phone=phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def generate_reset_token() -> str:
    """生成重置密码token"""
    return secrets.token_urlsafe(32)




def verify_reset_token(db: Session, token: str):
    """验证重置token"""
    user = db.query(models.User).filter(
        models.User.reset_token == token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()
    return user


def reset_password(db: Session, token: str, new_password: str):
    """重置密码"""
    user = verify_reset_token(db, token)
    if not user:
        raise ValueError("无效或过期的重置token")
    
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return user


def update_user(db: Session, user_id: int, user_update: dict):
    """更新用户信息"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")
    
    # 检查用户名是否已被其他用户使用
    if "username" in user_update and user_update["username"]:
        existing_user = db.query(models.User).filter(
            models.User.username == user_update["username"],
            models.User.id != user_id
        ).first()
        if existing_user:
            raise ValueError("用户名已被使用")
    
    # 检查手机号是否已被其他用户使用
    if "phone" in user_update and user_update["phone"]:
        phone = str(user_update["phone"]).strip() if user_update["phone"] else None
        if phone:
            existing_user = db.query(models.User).filter(
                models.User.phone == phone,
                models.User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("手机号已被使用")
            user_update["phone"] = phone
        else:
            user_update["phone"] = None
    
    # 更新字段
    # 注意：需要区分"未提供"和"设置为None"的情况
    # 对于可选字段（bio, nickname, location, phone, avatar），允许设置为None
    optional_fields = {"bio", "nickname", "location", "phone", "avatar"}
    
    for key, value in user_update.items():
        if key in optional_fields:
            # 可选字段：允许设置为None（清空）
            setattr(user, key, value)
        elif value is not None:
            # 必填字段（username, phone）：不允许设置为None
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, new_password: str):
    """更新用户密码"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")
    
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

