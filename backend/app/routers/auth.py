import os
from app import config  # Load local environment configuration.
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app import crud, schemas
from app.database import get_db
from app.services.sms_service import send_sms, check_sms_code

router = APIRouter(prefix="/api/auth", tags=["认证"])

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError("Set JWT_SECRET_KEY to a unique random value of at least 32 characters")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户（必需登录）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return schemas.UserResponse.model_validate(user)


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[schemas.UserResponse]:
    """
    获取当前用户（可选，支持游客模式）
    如果未提供token或token无效，返回None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except (JWTError, Exception):
        return None
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        return None
    return schemas.UserResponse.model_validate(user)


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        db_user = crud.create_user(db, user)
        return schemas.UserResponse.model_validate(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录（支持form-data和JSON）"""
    # 支持用户名或手机号登录
    user = crud.get_user_by_username_or_phone(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }


@router.post("/login-json", response_model=schemas.Token)
def login_json(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """用户登录（JSON格式）"""
    # 支持用户名或手机号登录
    user = crud.get_user_by_username_or_phone(db, login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not crud.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: schemas.UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/send-sms", response_model=schemas.MessageResponse)
def send_sms_code(request: schemas.SmsSendRequest):
    """发送短信验证码"""
    result = send_sms(request.phone, request.scene)
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )


@router.post("/register-with-sms", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_with_sms(user: schemas.UserCreateWithSms, db: Session = Depends(get_db)):
    """用户注册（带短信验证码）"""
    # 验证手机号
    if not user.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册时必须提供手机号"
        )
    
    # 验证手机号格式
    if not user.phone.startswith("1") or len(user.phone) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 验证验证码
    if not user.sms_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入验证码"
        )
    
    # 校验验证码
    verify_result = check_sms_code(user.phone, user.sms_code)
    if not verify_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verify_result["message"]
        )
    
    # 创建用户（使用UserCreate，不包含sms_code）
    user_create = schemas.UserCreate(
        username=user.username,
        phone=user.phone,
        password=user.password
    )
    
    try:
        db_user = crud.create_user(db, user_create)
        return schemas.UserResponse.model_validate(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reset-password-with-sms", response_model=schemas.MessageResponse)
def reset_password_with_sms(reset_data: schemas.PasswordResetWithSms, db: Session = Depends(get_db)):
    """重置密码（使用短信验证码）"""
    # 验证手机号格式
    if not reset_data.phone.startswith("1") or len(reset_data.phone) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 验证验证码
    if not reset_data.sms_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入验证码"
        )
    
    # 校验验证码
    verify_result = check_sms_code(reset_data.phone, reset_data.sms_code)
    if not verify_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verify_result["message"]
        )
    
    # 根据手机号查找用户
    user = crud.get_user_by_phone(db, reset_data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该手机号未注册"
        )
    
    # 重置密码
    try:
        crud.update_user_password(db, user.id, reset_data.new_password)
        return {"message": "密码重置成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

