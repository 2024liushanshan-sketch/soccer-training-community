"""
赛事中心相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models
from app.routers.auth import get_current_user
from app import schemas
from app.schemas_extended import (
    MatchResponse, MatchRegistrationCreate, MatchRegistrationResponse,
    MatchScheduleResponse, MatchPlayerResponse, MatchVoteCreate,
    MatchReplayResponse, MatchCheerCreate, MatchCheerResponse
)

router = APIRouter(prefix="/api/match", tags=["赛事中心"])


@router.get("/local", response_model=List[MatchResponse])
def get_local_matches(db: Session = Depends(get_db)):
    """获取本地赛事列表"""
    matches = db.query(models.Match).order_by(models.Match.date.desc()).all()
    return matches


@router.get("/registrations", response_model=dict)
def get_registrations(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取在线报名信息（当前用户可报名的赛事）"""
    # 获取最新的可报名赛事
    today = datetime.now().date()
    match = db.query(models.Match).filter(
        models.Match.date >= today,
        models.Match.status == "upcoming"
    ).order_by(models.Match.date.asc()).first()
    
    if not match:
        return {
            "title": "暂无可报名赛事",
            "desc": "请关注后续赛事通知",
            "status": "closed",
            "match_id": None
        }
    
    # 检查用户是否已报名
    existing_reg = db.query(models.MatchRegistration).filter(
        models.MatchRegistration.match_id == match.id,
        models.MatchRegistration.user_id == current_user.id
    ).first()
    
    # 判断报名是否截止（假设比赛前3天截止）
    from datetime import timedelta
    registration_deadline = match.date - timedelta(days=3)
    is_open = datetime.now().date() < registration_deadline and not existing_reg
    
    return {
        "title": match.name,
        "desc": f"比赛时间：{match.date.strftime('%Y年%m月%d日')} {match.time or ''}",
        "status": "open" if is_open else "closed",
        "match_id": match.id
    }


@router.post("/registrations", response_model=MatchRegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_registration(
    registration_data: MatchRegistrationCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交赛事报名"""
    # 检查赛事是否存在
    match = db.query(models.Match).filter(models.Match.id == registration_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="赛事不存在")
    
    # 检查是否已报名
    existing_reg = db.query(models.MatchRegistration).filter(
        models.MatchRegistration.match_id == registration_data.match_id,
        models.MatchRegistration.user_id == current_user.id
    ).first()
    
    if existing_reg:
        raise HTTPException(status_code=400, detail="您已报名该赛事")
    
    # 创建报名记录
    db_reg = models.MatchRegistration(
        match_id=registration_data.match_id,
        user_id=current_user.id,
        name=registration_data.name,
        phone=registration_data.phone,
        event=registration_data.event,
        status="pending"
    )
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)
    return db_reg


@router.get("/schedules", response_model=List[MatchScheduleResponse])
def get_schedules(db: Session = Depends(get_db), limit: int = 10):
    """获取赛程与战报列表"""
    schedules = db.query(models.MatchSchedule).order_by(
        models.MatchSchedule.id.desc()
    ).limit(limit).all()
    
    # 格式化日期显示
    result = []
    for schedule in schedules:
        # 解析日期字符串或使用match的日期
        match = db.query(models.Match).filter(models.Match.id == schedule.match_id).first()
        if match:
            date_obj = match.date if isinstance(match.date, datetime) else datetime.fromisoformat(str(match.date))
            day = date_obj.day
            month = f"{date_obj.month}月"
        else:
            day = schedule.day
            month = schedule.month
        
        result.append({
            "id": schedule.id,
            "match_id": schedule.match_id,
            "day": str(day),
            "month": month,
            "team_a": schedule.team_a,
            "team_b": schedule.team_b,
            "time": schedule.time,
            "score": schedule.score
        })
    
    return result


@router.get("/{match_id}/schedules", response_model=List[MatchScheduleResponse])
def get_match_schedules(match_id: int, db: Session = Depends(get_db)):
    """获取指定赛事的赛程"""
    schedules = db.query(models.MatchSchedule).filter(
        models.MatchSchedule.match_id == match_id
    ).order_by(models.MatchSchedule.id.desc()).all()
    
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    result = []
    for schedule in schedules:
        if match:
            date_obj = match.date if isinstance(match.date, datetime) else datetime.fromisoformat(str(match.date))
            day = date_obj.day
            month = f"{date_obj.month}月"
        else:
            day = schedule.day
            month = schedule.month
        
        result.append({
            "id": schedule.id,
            "match_id": schedule.match_id,
            "day": str(day),
            "month": month,
            "team_a": schedule.team_a,
            "team_b": schedule.team_b,
            "time": schedule.time,
            "score": schedule.score
        })
    
    return result



@router.get("/{match_id}/experience")
def get_match_experience(match_id: int, db: Session = Depends(get_db)):
    """获取比赛日体验数据（比赛信息、球员列表、回放、助威墙）"""
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="赛事不存在")
    
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).order_by(models.MatchPlayer.votes.desc()).all()
    
    replays = db.query(models.MatchReplay).filter(
        models.MatchReplay.match_id == match_id
    ).order_by(models.MatchReplay.id.desc()).all()
    
    cheers = db.query(models.MatchCheer).filter(
        models.MatchCheer.match_id == match_id
    ).order_by(models.MatchCheer.created_at.desc()).limit(20).all()
    
    return {
        "match": {
            "id": match.id,
            "name": match.name,
            "team_a": match.team_a,
            "team_b": match.team_b,
            "score_a": match.score_a or 0,
            "score_b": match.score_b or 0,
            "status": match.status,
            "time": match.time or ""
        },
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "position": p.position,
                "avatar": p.avatar or "/static/avatar.png",
                "votes": p.votes or 0
            }
            for p in players
        ],
        "replays": [
            {
                "id": r.id,
                "title": r.title,
                "duration": r.duration or "00:00",
                "time": r.time or "",
                "video_url": r.video_url or ""
            }
            for r in replays
        ],
        "cheers": [c.content for c in cheers]
    }


@router.get("/{match_id}/players", response_model=List[MatchPlayerResponse])
def get_match_players(
    match_id: int,
    current_user_id: Optional[int] = Query(None, description="当前用户ID（可选，用于检查是否已投票）"),
    db: Session = Depends(get_db)
):
    """获取比赛球员列表（支持检查用户是否已投票）"""
    players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).order_by(models.MatchPlayer.votes.desc()).all()
    
    result = []
    for player in players:
        voted = False
        if current_user_id:
            vote = db.query(models.MatchVote).filter(
                models.MatchVote.match_id == match_id,
                models.MatchVote.player_id == player.id,
                models.MatchVote.user_id == current_user_id
            ).first()
            voted = vote is not None
        
        result.append({
            "id": player.id,
            "match_id": player.match_id,
            "name": player.name,
            "position": player.position,
            "avatar": player.avatar or "/static/avatar.png",
            "votes": player.votes or 0,
            "voted": voted
        })
    
    return result


@router.post("/{match_id}/vote", response_model=dict)
def vote_player(
    match_id: int,
    vote_data: MatchVoteCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """为球员投票（MVP投票）"""
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="赛事不存在")
    
    player = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.id == vote_data.player_id,
        models.MatchPlayer.match_id == match_id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="球员不存在")
    
    existing_vote = db.query(models.MatchVote).filter(
        models.MatchVote.match_id == match_id,
        models.MatchVote.user_id == current_user.id
    ).first()
    
    if existing_vote:
        if existing_vote.player_id == vote_data.player_id:
            # 取消投票：删除投票记录，减少票数
            old_player = db.query(models.MatchPlayer).filter(
                models.MatchPlayer.id == existing_vote.player_id
            ).first()
            if old_player:
                old_player.votes = max(0, (old_player.votes or 0) - 1)
            db.delete(existing_vote)
            db.commit()
            db.refresh(old_player)
            return {"voted": False, "votes": old_player.votes or 0}
        
        # 更改投票：更新投票记录，更新两个球员的票数
        old_player = db.query(models.MatchPlayer).filter(
            models.MatchPlayer.id == existing_vote.player_id
        ).first()
        if old_player:
            old_player.votes = max(0, (old_player.votes or 0) - 1)
        existing_vote.player_id = vote_data.player_id
    else:
        # 新投票：创建投票记录
        new_vote = models.MatchVote(
            match_id=match_id,
            player_id=vote_data.player_id,
            user_id=current_user.id
        )
        db.add(new_vote)
    
    # 增加新投票球员的票数
    player.votes = (player.votes or 0) + 1
    db.commit()
    db.refresh(player)
    
    return {"voted": True, "votes": player.votes or 0}


@router.get("/{match_id}/replays", response_model=List[MatchReplayResponse])
def get_match_replays(match_id: int, db: Session = Depends(get_db)):
    """获取比赛回放列表"""
    replays = db.query(models.MatchReplay).filter(
        models.MatchReplay.match_id == match_id
    ).order_by(models.MatchReplay.id.desc()).all()
    
    return replays


@router.get("/{match_id}/cheers", response_model=List[MatchCheerResponse])
def get_match_cheers(match_id: int, db: Session = Depends(get_db), limit: int = 50):
    """获取助威墙列表"""
    cheers = db.query(models.MatchCheer).filter(
        models.MatchCheer.match_id == match_id
    ).order_by(models.MatchCheer.created_at.desc()).limit(limit).all()
    
    return cheers


@router.post("/{match_id}/cheers", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_cheer(
    match_id: int,
    cheer_data: MatchCheerCreate,
    db: Session = Depends(get_db)
):
    """发送助威语（支持匿名，不需要登录）"""
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="赛事不存在")
    
    db_cheer = models.MatchCheer(
        match_id=match_id,
        user_id=None,
        content=cheer_data.content
    )
    db.add(db_cheer)
    db.commit()
    db.refresh(db_cheer)
    
    return {"content": db_cheer.content, "id": db_cheer.id}
