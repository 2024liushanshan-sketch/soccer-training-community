"""
首页相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models
from app.routers.auth import get_current_user
from app.schemas_extended import BannerResponse, KnowledgeResponse, MatchResponse, AcademyVideoResponse

router = APIRouter(prefix="/api/home", tags=["首页"])


@router.get("/banners", response_model=List[BannerResponse])
def get_banners(db: Session = Depends(get_db)):
    """获取首页Banner列表"""
    banners = db.query(models.Banner).filter(models.Banner.is_active == True).order_by(models.Banner.sort_order).all()
    return banners


@router.get("/hot-matches", response_model=List[MatchResponse])
def get_hot_matches(db: Session = Depends(get_db), limit: int = 5):
    """获取热门赛事列表"""
    matches = db.query(models.Match).order_by(models.Match.date.desc()).limit(limit).all()
    return matches


@router.get("/recommended-videos", response_model=List[AcademyVideoResponse])
def get_recommended_videos(db: Session = Depends(get_db), limit: int = 6):
    """获取推荐视频列表"""
    videos = db.query(models.AcademyVideo).order_by(models.AcademyVideo.views.desc()).limit(limit).all()
    # 添加相对时间
    from datetime import datetime, timedelta
    for video in videos:
        delta = datetime.now() - video.created_at
        if delta.days == 0:
            video.date = "今天"
        elif delta.days == 1:
            video.date = "1天前"
        elif delta.days < 7:
            video.date = f"{delta.days}天前"
        else:
            video.date = f"{delta.days // 7}周前"
    return videos


@router.get("/knowledge", response_model=KnowledgeResponse)
def get_knowledge(db: Session = Depends(get_db)):
    """获取足球知识卡片"""
    knowledge = db.query(models.Knowledge).order_by(models.Knowledge.created_at.desc()).first()
    if not knowledge:
        # 返回默认知识
        return KnowledgeResponse(
            id=0,
            title="足球小知识",
            content="足球运动起源于中国古代的蹴鞠，现代足球规则于1863年在英国确立。"
        )
    return knowledge

