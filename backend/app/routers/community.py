"""
社区相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models
from app.routers.auth import get_current_user, get_optional_user
from app import schemas
from app.schemas_extended import (
    CommunityTopicResponse, CommunityPostResponse, CommunityPostCreate,
    CommunityCommentResponse, CommunityCommentCreate
)

router = APIRouter(prefix="/api/community", tags=["社区"])


@router.get("/topics", response_model=List[CommunityTopicResponse])
def get_topics(db: Session = Depends(get_db)):
    """获取话题列表"""
    topics = db.query(models.CommunityTopic).order_by(models.CommunityTopic.sort_order).all()
    return topics


@router.get("/nearby-friends")
def get_nearby_friends(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """获取附近球友列表（支持游客模式）"""
    # 游客模式返回空列表
    if not current_user:
        return []
    # 如果用户没有提供位置信息，使用当前用户的位置
    if latitude is None or longitude is None:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user and user.latitude and user.longitude:
            latitude = user.latitude
            longitude = user.longitude
        else:
            # 如果没有位置信息，返回所有用户（简化处理）
            users = db.query(models.User).filter(
                models.User.id != current_user.id
            ).limit(limit).all()
            
            result = []
            for u in users:
                result.append({
                    "id": u.id,
                    "name": u.nickname or u.username,
                    "avatar": u.avatar or "/static/avatar.png",
                    "distance": 0.0  # 无法计算距离
                })
            return result
    
    # 如果有位置信息，计算距离（简化版，实际应该使用地理距离计算）
    users = db.query(models.User).filter(
        models.User.id != current_user.id,
        models.User.latitude.isnot(None),
        models.User.longitude.isnot(None)
    ).limit(limit * 2).all()
    
    # 计算距离（简化版，使用曼哈顿距离）
    result = []
    for u in users:
        if u.latitude and u.longitude:
            # 简化的距离计算（实际应该使用Haversine公式）
            distance = abs(u.latitude - latitude) + abs(u.longitude - longitude)
            result.append({
                "id": u.id,
                "name": u.nickname or u.username,
                "avatar": u.avatar or "/static/avatar.png",
                "distance": round(distance * 111, 1)  # 粗略转换为km
            })
    
    # 按距离排序
    result.sort(key=lambda x: x["distance"])
    return result[:limit]


@router.get("/posts", response_model=List[CommunityPostResponse])
def get_posts(
    db: Session = Depends(get_db),
    topic_id: Optional[int] = Query(None, description="话题ID（可选）"),
    limit: int = Query(20, description="每页数量"),
    offset: int = Query(0, description="偏移量"),
    current_user_id: Optional[int] = Query(None, description="当前用户ID（可选，用于检查是否已点赞）")
):
    """获取社区动态列表（支持可选登录）"""
    query = db.query(models.CommunityPost)
    
    if topic_id:
        query = query.filter(models.CommunityPost.topic_id == topic_id)
    
    posts = query.order_by(models.CommunityPost.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for post in posts:
        user = db.query(models.User).filter(models.User.id == post.user_id).first()
        
        # 计算相对时间
        delta = datetime.now() - post.created_at
        if delta.days == 0:
            if delta.seconds < 3600:
                time_str = f"{delta.seconds // 60}分钟前"
            else:
                time_str = f"{delta.seconds // 3600}小时前"
        elif delta.days == 1:
            time_str = "1天前"
        else:
            time_str = f"{delta.days}天前"
        
        # 检查当前用户是否已点赞
        liked = False
        if current_user_id:
            like = db.query(models.CommunityLike).filter(
                models.CommunityLike.post_id == post.id,
                models.CommunityLike.user_id == current_user_id
            ).first()
            liked = like is not None
        
        # 获取话题信息
        topic_name = None
        if post.topic_id:
            topic = db.query(models.CommunityTopic).filter(models.CommunityTopic.id == post.topic_id).first()
            if topic:
                topic_name = topic.name
        
        result.append({
            "id": post.id,
            "user_id": post.user_id,
            "topic_id": post.topic_id,
            "content": post.content,
            "images": post.images.split(",") if post.images else [],
            "likes": post.likes,
            "comments": post.comments,
            "created_at": post.created_at,
            "user": {
                "id": user.id if user else 0,
                "name": user.nickname or user.username if user else "未知",
                "avatar": user.avatar or "/static/avatar.png" if user else "/static/avatar.png"
            },
            "time": time_str,
            "topic": topic_name,
            "liked": liked
        })
    
    return result


@router.post("/posts", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: CommunityPostCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布社区动态"""
    db_post = models.CommunityPost(
        user_id=current_user.id,
        topic_id=post_data.topic_id,
        content=post_data.content,
        images=",".join(post_data.images) if post_data.images else None,
        likes=0,
        comments=0
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    topic_name = None
    if post_data.topic_id:
        topic = db.query(models.CommunityTopic).filter(models.CommunityTopic.id == post_data.topic_id).first()
        if topic:
            topic_name = topic.name
    
    return {
        "id": db_post.id,
        "user": {
            "id": user.id if user else 0,
            "name": user.nickname or user.username if user else "未知",
            "avatar": user.avatar or "/static/avatar.png" if user else "/static/avatar.png"
        },
        "time": "刚刚",
        "content": db_post.content,
        "images": post_data.images or [],
        "topic": topic_name,
        "likes": 0,
        "liked": False,
        "comments": 0
    }


@router.post("/posts/{post_id}/like", response_model=dict)
def toggle_like(
    post_id: int,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞动态"""
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")
    
    # 检查是否已点赞
    like = db.query(models.CommunityLike).filter(
        models.CommunityLike.post_id == post_id,
        models.CommunityLike.user_id == current_user.id
    ).first()
    
    if like:
        # 取消点赞
        db.delete(like)
        post.likes = max(0, post.likes - 1)
        liked = False
    else:
        # 点赞
        new_like = models.CommunityLike(
            post_id=post_id,
            user_id=current_user.id
        )
        db.add(new_like)
        post.likes += 1
        liked = True
    
    db.commit()
    
    return {
        "liked": liked,
        "likes": post.likes
    }


@router.get("/posts/{post_id}/comments", response_model=List[CommunityCommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取动态的评论列表"""
    comments = db.query(models.CommunityComment).filter(
        models.CommunityComment.post_id == post_id
    ).order_by(models.CommunityComment.created_at.asc()).limit(limit).all()
    
    result = []
    for comment in comments:
        user = db.query(models.User).filter(models.User.id == comment.user_id).first()
        result.append({
            "id": comment.id,
            "name": user.nickname or user.username if user else "未知",
            "avatar": user.avatar or "/static/avatar.png" if user else "/static/avatar.png",
            "text": comment.content
        })
    
    return result


@router.post("/posts/{post_id}/comments", response_model=CommunityCommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_data: CommunityCommentCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发表评论"""
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")
    
    db_comment = models.CommunityComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    db.add(db_comment)
    
    # 更新动态的评论数
    post.comments += 1
    
    db.commit()
    db.refresh(db_comment)
    
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    return {
        "id": db_comment.id,
        "name": user.nickname or user.username if user else "未知",
        "avatar": user.avatar or "/static/avatar.png" if user else "/static/avatar.png",
        "text": db_comment.content
    }

