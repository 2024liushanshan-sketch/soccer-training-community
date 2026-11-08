"""
健康营养相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app import models
from app.routers.auth import get_current_user
from app import schemas
from app.schemas_extended import (
    HealthNutritionGuideResponse, HealthSleepDataResponse,
    HealthInjuryPreventionResponse, HealthMonitorDataResponse
)

router = APIRouter(prefix="/api/health", tags=["健康营养"])


@router.get("/nutrition-guides", response_model=List[HealthNutritionGuideResponse])
def get_nutrition_guides(db: Session = Depends(get_db)):
    """获取营养指南列表"""
    guides = db.query(models.HealthNutritionGuide).order_by(
        models.HealthNutritionGuide.sort_order
    ).all()
    
    return guides


@router.get("/nutrition-guides/{guide_id}", response_model=HealthNutritionGuideResponse)
def get_nutrition_guide(guide_id: int, db: Session = Depends(get_db)):
    """获取营养指南详情"""
    guide = db.query(models.HealthNutritionGuide).filter(
        models.HealthNutritionGuide.id == guide_id
    ).first()
    
    if not guide:
        raise HTTPException(status_code=404, detail="营养指南不存在")
    
    return guide


@router.get("/sleep-data", response_model=HealthSleepDataResponse)
def get_sleep_data(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    target_date: Optional[str] = None
):
    """获取睡眠数据（默认获取昨日数据）"""
    # 如果没有指定日期，获取昨天的数据
    if target_date:
        try:
            target = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
        except:
            target = date.today()
    else:
        from datetime import timedelta
        target = date.today() - timedelta(days=1)
    
    sleep_data = db.query(models.HealthSleepData).filter(
        models.HealthSleepData.user_id == current_user.id,
        models.HealthSleepData.date == target
    ).first()
    
    if not sleep_data:
        # 返回默认数据
        return {
            "id": 0,
            "hours": 0.0,
            "quality": "无数据",
            "goal_hours": 9.0
        }
    
    return {
        "id": sleep_data.id,
        "hours": sleep_data.hours,
        "quality": sleep_data.quality or "良好",
        "goal_hours": sleep_data.goal_hours or 9.0
    }


@router.get("/sleep-tips")
def get_sleep_tips():
    """获取睡眠小贴士"""
    return {
        "tip": "青少年建议每天睡眠8-10小时，保证充足休息有助于运动表现和身体恢复。"
    }


@router.get("/injury-prevention", response_model=List[HealthInjuryPreventionResponse])
def get_injury_prevention(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取运动损伤预防与康复列表"""
    items = db.query(models.HealthInjuryPrevention).order_by(
        models.HealthInjuryPrevention.sort_order
    ).all()
    
    result = []
    for item in items:
        # 检查用户是否已收藏
        collection = db.query(models.HealthInjuryCollection).filter(
            models.HealthInjuryCollection.user_id == current_user.id,
            models.HealthInjuryCollection.injury_id == item.id
        ).first()
        
        result.append({
            "id": item.id,
            "title": item.title,
            "desc": item.desc,
            "content": item.content,
            "icon": item.icon or "🏥",
            "collected": collection is not None
        })
    
    return result


@router.post("/injury-prevention/{injury_id}/collect", response_model=dict)
def toggle_collect(
    injury_id: int,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏/取消收藏运动损伤预防内容"""
    injury = db.query(models.HealthInjuryPrevention).filter(
        models.HealthInjuryPrevention.id == injury_id
    ).first()
    
    if not injury:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    # 检查是否已收藏
    collection = db.query(models.HealthInjuryCollection).filter(
        models.HealthInjuryCollection.user_id == current_user.id,
        models.HealthInjuryCollection.injury_id == injury_id
    ).first()
    
    if collection:
        # 取消收藏
        db.delete(collection)
        collected = False
    else:
        # 收藏
        new_collection = models.HealthInjuryCollection(
            user_id=current_user.id,
            injury_id=injury_id
        )
        db.add(new_collection)
        collected = True
    
    db.commit()
    
    return {"collected": collected}


@router.get("/monitor-data", response_model=HealthMonitorDataResponse)
def get_monitor_data(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    target_date: Optional[str] = None
):
    """获取健康监测数据（默认获取今日数据）"""
    # 如果没有指定日期，获取今天的数据
    if target_date:
        try:
            target = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
        except:
            target = date.today()
    else:
        target = date.today()
    
    monitor_data = db.query(models.HealthMonitorData).filter(
        models.HealthMonitorData.user_id == current_user.id,
        models.HealthMonitorData.date == target
    ).first()
    
    if not monitor_data:
        # 返回默认数据（表示未连接设备）
        return {
            "id": 0,
            "steps": 0,
            "heart_rate": None,
            "calories": 0,
            "connected": False
        }
    
    return {
        "id": monitor_data.id,
        "steps": monitor_data.steps or 0,
        "heart_rate": monitor_data.heart_rate,
        "calories": monitor_data.calories or 0,
        "connected": True
    }


@router.post("/monitor-data", response_model=HealthMonitorDataResponse, status_code=status.HTTP_201_CREATED)
def create_monitor_data(
    data: dict,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建或更新健康监测数据（模拟连接设备）"""
    today = date.today()
    
    monitor_data = db.query(models.HealthMonitorData).filter(
        models.HealthMonitorData.user_id == current_user.id,
        models.HealthMonitorData.date == today
    ).first()
    
    if monitor_data:
        # 更新现有数据
        if "steps" in data:
            monitor_data.steps = data["steps"]
        if "heart_rate" in data:
            monitor_data.heart_rate = data["heart_rate"]
        if "calories" in data:
            monitor_data.calories = data["calories"]
    else:
        # 创建新数据
        monitor_data = models.HealthMonitorData(
            user_id=current_user.id,
            date=today,
            steps=data.get("steps", 0),
            heart_rate=data.get("heart_rate"),
            calories=data.get("calories", 0)
        )
        db.add(monitor_data)
    
    db.commit()
    db.refresh(monitor_data)
    
    return {
        "id": monitor_data.id,
        "steps": monitor_data.steps or 0,
        "heart_rate": monitor_data.heart_rate,
        "calories": monitor_data.calories or 0,
        "connected": True
    }

