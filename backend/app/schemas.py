from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    phone: str = Field(..., max_length=20, description="手机号")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    avatar: Optional[str] = None
    bio: Optional[str] = None
    nickname: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    location: Optional[str] = Field(None, max_length=100, description="位置")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str


class SmsSendRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    scene: str = Field(..., description="场景：register/login/reset_password等")


class SmsVerifyRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")


class UserCreateWithSms(UserCreate):
    sms_code: Optional[str] = Field(None, description="短信验证码")


class PasswordResetWithSms(BaseModel):
    phone: str = Field(..., description="手机号")
    sms_code: str = Field(..., description="短信验证码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

