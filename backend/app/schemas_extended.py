"""
扩展的Pydantic模型定义
由于代码量较大，将新增的schemas放在单独文件中
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 首页相关 ====================
class BannerResponse(BaseModel):
    id: int
    title: str
    desc: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class KnowledgeResponse(BaseModel):
    id: int
    title: str
    content: str
    
    class Config:
        from_attributes = True


# ==================== 赛事相关 ====================
class MatchResponse(BaseModel):
    id: int
    name: str
    date: datetime
    time: Optional[str] = None
    location: Optional[str] = None
    status: str
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    
    class Config:
        from_attributes = True


class MatchRegistrationCreate(BaseModel):
    match_id: int
    name: str
    phone: str
    event: Optional[str] = None


class MatchRegistrationResponse(BaseModel):
    id: int
    match_id: int
    name: str
    phone: str
    event: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchScheduleResponse(BaseModel):
    id: int
    match_id: int
    day: str
    month: str
    team_a: str
    team_b: str
    time: Optional[str] = None
    score: Optional[str] = None
    
    class Config:
        from_attributes = True


class MatchPlayerResponse(BaseModel):
    id: int
    match_id: int
    name: str
    position: str
    avatar: Optional[str] = None
    votes: int
    voted: Optional[bool] = False  # 当前用户是否已投票
    
    class Config:
        from_attributes = True


class MatchVoteCreate(BaseModel):
    match_id: int
    player_id: int


class MatchReplayResponse(BaseModel):
    id: int
    match_id: int
    title: str
    duration: Optional[str] = None
    video_url: Optional[str] = None
    time: Optional[str] = None
    
    class Config:
        from_attributes = True


class MatchCheerCreate(BaseModel):
    match_id: int
    content: str


class MatchCheerResponse(BaseModel):
    id: int
    match_id: int
    user_id: Optional[int] = None
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 训练相关 ====================
class TrainingPlanCreate(BaseModel):
    date: datetime
    time: str
    title: str
    desc: Optional[str] = None


class TrainingPlanUpdate(BaseModel):
    date: Optional[datetime] = None
    time: Optional[str] = None
    title: Optional[str] = None
    desc: Optional[str] = None
    completed: Optional[bool] = None


class TrainingPlanResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    time: str
    title: str
    desc: Optional[str] = None
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrainingStatResponse(BaseModel):
    id: int
    user_id: int
    week_start: datetime
    total_days: int
    total_hours: float
    completion_rate: float
    
    class Config:
        from_attributes = True


class CoachPostCreate(BaseModel):
    content: str


class CoachPostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    likes: int
    comments: int
    created_at: datetime
    author: Optional[str] = None  # 发布者用户名
    time: Optional[str] = None  # 相对时间
    
    class Config:
        from_attributes = True


# ==================== 社区相关 ====================
class CommunityTopicResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class CommunityPostCreate(BaseModel):
    topic_id: Optional[int] = None
    content: str
    images: Optional[List[str]] = None


class CommunityPostResponse(BaseModel):
    id: int
    user_id: int
    topic_id: Optional[int] = None
    content: str
    images: Optional[List[str]] = None
    likes: int
    comments: int
    created_at: datetime
    user: Optional[dict] = None  # 用户信息
    topic: Optional[str] = None  # 话题名称
    liked: Optional[bool] = False  # 当前用户是否已点赞
    time: Optional[str] = None  # 相对时间
    
    class Config:
        from_attributes = True


class CommunityCommentCreate(BaseModel):
    post_id: int
    content: str


class CommunityCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    name: Optional[str] = None  # 评论者名称
    avatar: Optional[str] = None  # 评论者头像
    
    class Config:
        from_attributes = True


class NearbyFriendResponse(BaseModel):
    id: int
    name: str
    avatar: Optional[str] = None
    distance: float
    
    class Config:
        from_attributes = True


# ==================== 技术学院相关 ====================
class AcademyCategoryResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class AcademyVideoResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    title: str
    cover: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[str] = None
    desc: Optional[str] = None
    views: int
    created_at: datetime
    date: Optional[str] = None  # 相对时间
    
    class Config:
        from_attributes = True


class AcademyChallengeResponse(BaseModel):
    id: int
    title: str
    desc: Optional[str] = None
    is_daily: bool
    completed: Optional[bool] = False  # 当前用户是否完成
    
    class Config:
        from_attributes = True


class AcademyPersonalPlanResponse(BaseModel):
    id: int
    user_id: int
    title: str
    desc: Optional[str] = None
    progress: float
    
    class Config:
        from_attributes = True


class AcademyPersonalPlanCreate(BaseModel):
    title: str
    desc: Optional[str] = None
    progress: Optional[float] = 0.0


# ==================== 健康与营养相关 ====================
class HealthNutritionGuideResponse(BaseModel):
    id: int
    icon: Optional[str] = None
    title: str
    desc: Optional[str] = None
    content: Optional[str] = None
    
    class Config:
        from_attributes = True


class HealthSleepDataCreate(BaseModel):
    date: datetime
    hours: float
    quality: Optional[str] = None
    goal_hours: Optional[float] = 9.0


class HealthSleepDataResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    hours: float
    quality: Optional[str] = None
    goal_hours: float
    
    class Config:
        from_attributes = True


class HealthInjuryPreventionResponse(BaseModel):
    id: int
    icon: Optional[str] = None
    title: str
    desc: Optional[str] = None
    content: Optional[str] = None
    collected: Optional[bool] = False  # 当前用户是否收藏
    
    class Config:
        from_attributes = True


class HealthMonitorDataCreate(BaseModel):
    date: datetime
    steps: Optional[int] = 0
    heart_rate: Optional[int] = None
    calories: Optional[int] = 0
    device_id: Optional[str] = None


class HealthMonitorDataResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    steps: int
    heart_rate: Optional[int] = None
    calories: int
    
    class Config:
        from_attributes = True


