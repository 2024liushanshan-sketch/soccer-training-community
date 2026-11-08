"""
训练中心相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app import models
from app.routers.auth import get_current_user, get_optional_user
from app import schemas
from app.schemas_extended import (
    TrainingPlanResponse, TrainingPlanCreate, TrainingPlanUpdate,
    TrainingStatResponse, CoachPostResponse, CoachPostCreate
)

router = APIRouter(prefix="/api/training", tags=["训练中心"])


@router.get("/plans", response_model=List[TrainingPlanResponse])
def get_training_plans(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db),
    date: Optional[str] = None
):
    """获取训练计划列表（支持日期筛选，支持游客模式）"""
    # 游客模式返回空列表
    if not current_user:
        return []
    
    query = db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == current_user.id)
    
    if date:
        try:
            date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
            query = query.filter(models.TrainingPlan.date >= date_obj.date())
        except:
            pass
    
    plans = query.order_by(models.TrainingPlan.date.desc(), models.TrainingPlan.time).all()
    return plans


@router.post("/plans", response_model=TrainingPlanResponse, status_code=status.HTTP_201_CREATED)
def create_training_plan(
    plan_data: TrainingPlanCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建训练计划"""
    db_plan = models.TrainingPlan(
        user_id=current_user.id,
        date=plan_data.date,
        time=plan_data.time,
        title=plan_data.title,
        desc=plan_data.desc,
        completed=False
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.put("/plans/{plan_id}", response_model=TrainingPlanResponse)
def update_training_plan(
    plan_id: int,
    plan_update: TrainingPlanUpdate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新训练计划"""
    plan = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.id == plan_id,
        models.TrainingPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")
    
    if plan_update.date is not None:
        plan.date = plan_update.date
    if plan_update.time is not None:
        plan.time = plan_update.time
    if plan_update.title is not None:
        plan.title = plan_update.title
    if plan_update.desc is not None:
        plan.desc = plan_update.desc
    if plan_update.completed is not None:
        plan.completed = plan_update.completed
    
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_plan(
    plan_id: int,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除训练计划"""
    plan = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.id == plan_id,
        models.TrainingPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")
    
    db.delete(plan)
    db.commit()
    return None


@router.post("/plans/{plan_id}/check", response_model=TrainingPlanResponse)
def check_training_plan(
    plan_id: int,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """训练计划打卡"""
    plan = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.id == plan_id,
        models.TrainingPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")
    
    plan.completed = not plan.completed
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/stats", response_model=TrainingStatResponse)
def get_training_stats(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取训练统计数据（本周训练天数、时长、完成率等，支持游客模式）"""
    # 游客模式返回默认数据
    if not current_user:
        from datetime import datetime
        return TrainingStatResponse(
            id=0,
            user_id=0,
            week_start=datetime.now().date(),
            total_days=0,
            total_hours=0.0,
            completion_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    # 计算本周的开始日期（周一）
    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    
    # 查询本周的训练计划
    week_end = week_start + timedelta(days=6)
    plans = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.user_id == current_user.id,
        models.TrainingPlan.date >= week_start,
        models.TrainingPlan.date <= week_end
    ).all()
    
    # 计算统计数据
    total_days = len(set(plan.date for plan in plans))
    completed_plans = [p for p in plans if p.completed]
    completion_rate = (len(completed_plans) / len(plans) * 100) if plans else 0
    
    # 假设每个训练计划平均1小时（实际应该从计划中获取）
    total_hours = len(completed_plans) * 1.0
    
    # 检查是否已有本周统计记录
    stat = db.query(models.TrainingStat).filter(
        models.TrainingStat.user_id == current_user.id,
        models.TrainingStat.week_start == week_start
    ).first()
    
    if stat:
        stat.total_days = total_days
        stat.total_hours = total_hours
        stat.completion_rate = completion_rate
    else:
        stat = models.TrainingStat(
            user_id=current_user.id,
            week_start=week_start,
            total_days=total_days,
            total_hours=total_hours,
            completion_rate=completion_rate
        )
        db.add(stat)
    
    db.commit()
    db.refresh(stat)
    return stat


@router.get("/analysis")
def get_training_analysis(
    current_user: Optional[schemas.UserResponse] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取数据分析数据"""
    # 获取本周统计
    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    plans = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.user_id == current_user.id,
        models.TrainingPlan.date >= week_start,
        models.TrainingPlan.date <= week_end
    ).all()
    
    completed_plans = [p for p in plans if p.completed]
    total_hours = len(completed_plans) * 1.0
    completion_rate = (len(completed_plans) / len(plans) * 100) if plans else 0
    
    # 获取上周统计用于对比
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    last_week_plans = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.user_id == current_user.id,
        models.TrainingPlan.date >= last_week_start,
        models.TrainingPlan.date <= last_week_end
    ).all()
    last_week_completed = len([p for p in last_week_plans if p.completed])
    last_week_completion_rate = (last_week_completed / len(last_week_plans) * 100) if last_week_plans else 0
    
    completion_change = completion_rate - last_week_completion_rate
    
    return [
        {
            "id": 1,
            "title": "训练时长",
            "value": f"{total_hours}小时",
            "desc": "本周累计"
        },
        {
            "id": 2,
            "title": "完成率",
            "value": f"{completion_rate:.0f}%",
            "desc": f"较上周{'提升' if completion_change > 0 else '下降'}{abs(completion_change):.0f}%"
        },
        {
            "id": 3,
            "title": "平均得分",
            "value": f"{completion_rate / 10:.1f}分",
            "desc": "训练质量评分"
        }
    ]


@router.get("/coach-posts", response_model=List[CoachPostResponse])
def get_coach_posts(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """获取教练社区动态列表"""
    posts = db.query(models.CoachPost).order_by(models.CoachPost.created_at.desc()).limit(limit).all()
    
    # 添加作者信息和相对时间
    from datetime import datetime
    result = []
    for post in posts:
        user = db.query(models.User).filter(models.User.id == post.user_id).first()
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
        
        result.append({
            "id": post.id,
            "user_id": post.user_id,
            "content": post.content,
            "likes": post.likes,
            "comments": post.comments,
            "created_at": post.created_at,
            "author": user.nickname or user.username if user else "未知",
            "time": time_str
        })
    
    return result


@router.post("/coach-posts", response_model=CoachPostResponse, status_code=status.HTTP_201_CREATED)
def create_coach_post(
    post_data: CoachPostCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布教练社区动态"""
    db_post = models.CoachPost(
        user_id=current_user.id,
        content=post_data.content,
        likes=0,
        comments=0
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    return {
        "id": db_post.id,
        "user_id": db_post.user_id,
        "content": db_post.content,
        "likes": db_post.likes,
        "comments": db_post.comments,
        "created_at": db_post.created_at,
        "author": user.nickname or user.username if user else "未知",
        "time": "刚刚"
    }


@router.get("/coach-posts/{post_id}", response_model=CoachPostResponse)
def get_coach_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """获取教练社区动态详情"""
    post = db.query(models.CoachPost).filter(models.CoachPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")
    
    user = db.query(models.User).filter(models.User.id == post.user_id).first()
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
    
    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "likes": post.likes,
        "comments": post.comments,
        "created_at": post.created_at,
        "author": user.nickname or user.username if user else "未知",
        "time": time_str
    }

