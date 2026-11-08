"""
技术学院相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models
from app.routers.auth import get_current_user
from app import schemas
from app.schemas_extended import (
    AcademyCategoryResponse, AcademyVideoResponse,
    AcademyChallengeResponse, AcademyPersonalPlanResponse
)

router = APIRouter(prefix="/api/academy", tags=["技术学院"])


@router.get("/categories", response_model=List[AcademyCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """获取视频分类列表"""
    categories = db.query(models.AcademyCategory).order_by(models.AcademyCategory.sort_order).all()
    return categories


@router.get("/videos", response_model=List[AcademyVideoResponse])
def get_videos(
    db: Session = Depends(get_db),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """获取视频列表（支持分类筛选和搜索）"""
    query = db.query(models.AcademyVideo)
    
    if category_id:
        query = query.filter(models.AcademyVideo.category_id == category_id)
    
    if keyword:
        query = query.filter(models.AcademyVideo.title.like(f"%{keyword}%"))
    
    videos = query.order_by(models.AcademyVideo.created_at.desc()).offset(offset).limit(limit).all()
    
    # 添加相对时间
    result = []
    for video in videos:
        delta = datetime.now() - video.created_at
        if delta.days == 0:
            date_str = "今天"
        elif delta.days == 1:
            date_str = "1天前"
        elif delta.days < 7:
            date_str = f"{delta.days}天前"
        else:
            date_str = f"{delta.days // 7}周前"
        
        result.append({
            "id": video.id,
            "title": video.title,
            "cover": video.cover or "/static/video-default.jpg",
            "duration": video.duration or "00:00",
            "views": video.views or 0,
            "date": date_str,
            "category": video.category_id,
            "url": video.url or "",
            "desc": video.desc or ""
        })
    
    return result


@router.get("/videos/{video_id}", response_model=AcademyVideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """获取视频详情"""
    video = db.query(models.AcademyVideo).filter(models.AcademyVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    # 增加观看次数
    video.views = (video.views or 0) + 1
    db.commit()
    db.refresh(video)
    
    delta = datetime.now() - video.created_at
    if delta.days == 0:
        date_str = "今天"
    elif delta.days == 1:
        date_str = "1天前"
    elif delta.days < 7:
        date_str = f"{delta.days}天前"
    else:
        date_str = f"{delta.days // 7}周前"
    
    return {
        "id": video.id,
        "title": video.title,
        "cover": video.cover or "/static/video-default.jpg",
        "duration": video.duration or "00:00",
        "views": video.views or 0,
        "date": date_str,
        "category": video.category_id,
        "url": video.url or "",
        "desc": video.desc or ""
    }


@router.get("/personal-plan", response_model=AcademyPersonalPlanResponse)
def get_personal_plan(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化训练计划"""
    plan = db.query(models.AcademyPersonalPlan).filter(
        models.AcademyPersonalPlan.user_id == current_user.id
    ).order_by(models.AcademyPersonalPlan.created_at.desc()).first()
    
    if not plan:
        # 返回默认计划
        return {
            "id": 0,
            "title": "本周训练计划",
            "desc": "针对你的技术水平制定的个性化训练方案",
            "progress": 0
        }
    
    # 计算完成进度（简化版，实际应该根据训练记录计算）
    progress = plan.progress or 0
    
    return {
        "id": plan.id,
        "title": plan.title or "本周训练计划",
        "desc": plan.desc or "针对你的技术水平制定的个性化训练方案",
        "progress": progress
    }


@router.get("/challenges", response_model=List[AcademyChallengeResponse])
def get_challenges(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """获取挑战任务列表"""
    challenges = db.query(models.AcademyChallenge).order_by(
        models.AcademyChallenge.created_at.desc()
    ).limit(limit).all()
    
    return challenges


@router.get("/challenges/daily", response_model=List[dict])
def get_daily_challenges(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日挑战任务"""
    # 获取今日的挑战任务
    today = datetime.now().date()
    challenges = db.query(models.AcademyChallenge).filter(
        models.AcademyChallenge.is_active == True
    ).limit(5).all()
    
    result = []
    for challenge in challenges:
        # 检查用户是否已完成
        record = db.query(models.AcademyChallengeRecord).filter(
            models.AcademyChallengeRecord.challenge_id == challenge.id,
            models.AcademyChallengeRecord.user_id == current_user.id,
            models.AcademyChallengeRecord.completed == True
        ).first()
        
        result.append({
            "id": challenge.id,
            "text": challenge.title or challenge.desc or "挑战任务",
            "completed": record is not None
        })
    
    return result


@router.post("/challenges/{challenge_id}/complete", response_model=dict)
def complete_challenge(
    challenge_id: int,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成挑战任务"""
    challenge = db.query(models.AcademyChallenge).filter(
        models.AcademyChallenge.id == challenge_id
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="挑战任务不存在")
    
    # 检查是否已完成
    record = db.query(models.AcademyChallengeRecord).filter(
        models.AcademyChallengeRecord.challenge_id == challenge_id,
        models.AcademyChallengeRecord.user_id == current_user.id
    ).first()
    
    if record:
        if record.completed:
            return {"message": "挑战已完成", "completed": True}
        record.completed = True
        record.completed_at = datetime.now()
    else:
        record = models.AcademyChallengeRecord(
            challenge_id=challenge_id,
            user_id=current_user.id,
            completed=True,
            completed_at=datetime.now()
        )
        db.add(record)
    
    db.commit()
    
    return {"message": "挑战完成", "completed": True}

