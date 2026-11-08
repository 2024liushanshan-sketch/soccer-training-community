from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.routers.auth import get_optional_user
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path
from app import crud, schemas, models
from app.database import get_db
from app.routers.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/profile", tags=["个人资料"])


@router.options("/avatar")
async def options_avatar():
    """处理CORS预检请求"""
    return {"message": "OK"}

# 文件上传配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def get_upload_path(filename: str) -> Path:
    """获取文件上传路径"""
    return UPLOAD_DIR / filename


def save_upload_file(file: UploadFile, user_id: int) -> str:
    """保存上传的文件，返回相对路径"""
    # 获取文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # 生成唯一文件名
    filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = get_upload_path(filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回相对路径（用于数据库存储）
    return f"uploads/avatars/{filename}"


def delete_old_avatar(avatar_path: str):
    """删除旧头像文件"""
    if avatar_path:
        file_path = Path(__file__).parent.parent.parent / avatar_path
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass  # 忽略删除错误


@router.get("/me", response_model=schemas.UserResponse)
def get_profile(current_user: Optional[schemas.UserResponse] = Depends(get_optional_user)):
    """获取当前用户资料（支持游客模式）"""
    # 游客模式返回示例用户信息
    if not current_user:
        return schemas.UserResponse(
            id=0,
            username="guest_user",
            phone="00000000000",
            is_active=True,
            created_at=datetime.now(),
            nickname="游客用户",
            bio="游客模式，登录后查看完整信息",
            location="",
            avatar=None
        )
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_profile(
    user_update: schemas.UserUpdate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    try:
        # 构建更新字典
        # 使用 model_dump(exclude_unset=True) 来只获取实际提供的字段
        # 这样可以区分"未提供"和"设置为None"
        update_dict = user_update.model_dump(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有要更新的字段"
            )
        
        # 构建更新数据字典
        update_data = {}
        
        # 必填字段：只有提供了非None值才更新
        if "username" in update_dict and update_dict["username"] is not None:
            update_data["username"] = update_dict["username"]
        if "phone" in update_dict and update_dict["phone"] is not None:
            update_data["phone"] = update_dict["phone"]
        
        # 可选字段：允许设置为None（清空）
        optional_fields = ["bio", "nickname", "location"]
        for key in optional_fields:
            if key in update_dict:
                update_data[key] = update_dict[key]  # 允许None值
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有要更新的字段"
            )
        
        updated_user = crud.update_user(db, current_user.id, update_data)
        return schemas.UserResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/avatar", response_model=schemas.UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传头像"""
    try:
        # 检查文件名
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件名不能为空"
            )
        
        # 读取文件内容
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件不能为空"
            )
        
        # 获取文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 删除旧头像
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if user.avatar:
            delete_old_avatar(user.avatar)
        
        # 生成唯一文件名
        filename = f"{current_user.id}_{uuid.uuid4().hex}{file_ext}"
        file_path = get_upload_path(filename)
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # 返回相对路径（用于数据库存储）
        avatar_path = f"uploads/avatars/{filename}"
        
        # 更新数据库
        updated_user = crud.update_user(db, current_user.id, {"avatar": avatar_path})
        return schemas.UserResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"上传头像错误: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.get("/avatar/{filename}")
def get_avatar(filename: str):
    """获取头像文件"""
    file_path = get_upload_path(filename)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="头像文件不存在"
        )
    return FileResponse(file_path)


@router.get("/stats")
def get_profile_stats(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取用户统计数据（支持游客模式）"""
    # 游客模式返回示例数据
    if not current_user:
        return {
            "matches": 0,
            "goals": 0,
            "assists": 0
        }
    
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "matches": user.matches_count or 0,
        "goals": user.goals_count or 0,
        "assists": user.assists_count or 0
    }


@router.get("/growth-records")
def get_growth_records(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """获取成长记录列表（支持游客模式）"""
    # 游客模式返回空列表
    if not current_user:
        return []
    
    records = db.query(models.UserGrowthRecord).filter(
        models.UserGrowthRecord.user_id == current_user.id
    ).order_by(models.UserGrowthRecord.date.desc()).limit(limit).all()
    
    return [
        {
            "id": record.id,
            "date": record.date.strftime("%Y-%m-%d") if isinstance(record.date, datetime) else str(record.date),
            "event": record.event
        }
        for record in records
    ]


@router.get("/skills")
def get_user_skills(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取用户技能评分（支持游客模式）"""
    # 游客模式返回默认技能（全0）
    if not current_user:
        return [
            {"name": "射门", "score": 0},
            {"name": "传球", "score": 0},
            {"name": "控球", "score": 0},
            {"name": "防守", "score": 0},
            {"name": "速度", "score": 0}
        ]
    
    skills = db.query(models.UserSkill).filter(
        models.UserSkill.user_id == current_user.id
    ).all()
    
    if not skills:
        # 返回默认技能（如果用户还没有技能数据）
        return [
            {"name": "射门", "score": 0},
            {"name": "传球", "score": 0},
            {"name": "控球", "score": 0},
            {"name": "防守", "score": 0}
        ]
    
    return [
        {"name": skill.skill_name, "score": skill.score}
        for skill in skills
    ]


@router.get("/weekly-training")
def get_weekly_training(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db),
    weeks: int = 7
):
    """获取过去N周的训练时长数据（支持游客模式）"""
    # 游客模式返回空数据
    if not current_user:
        return []
    
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    days_since_monday = today.weekday()
    current_week_start = today - timedelta(days=days_since_monday)
    
    result = []
    for i in range(weeks - 1, -1, -1):
        week_start = current_week_start - timedelta(days=7 * i)
        week_end = week_start + timedelta(days=6)
        
        # 查询该周的训练统计
        stat = db.query(models.TrainingStat).filter(
            models.TrainingStat.user_id == current_user.id,
            models.TrainingStat.week_start == week_start
        ).first()
        
        hours = stat.total_hours if stat else 0
        
        # 生成周标签
        if i == 0:
            week_label = "本周"
        elif i == 1:
            week_label = "上周"
        else:
            week_label = f"{i}周前"
        
        result.append({
            "week": week_label,
            "hours": hours
        })
    
    return result

