from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ==================== 用户相关 ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="加密后的密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 个人资料相关字段
    avatar = Column(String(255), nullable=True, comment="头像路径")
    bio = Column(String(500), nullable=True, comment="个人简介")
    nickname = Column(String(50), nullable=True, comment="昵称")
    location = Column(String(100), nullable=True, comment="位置")
    latitude = Column(Float, nullable=True, comment="纬度")
    longitude = Column(Float, nullable=True, comment="经度")
    
    # 忘记密码相关字段
    reset_token = Column(String(255), nullable=True, comment="重置密码token")
    reset_token_expires = Column(DateTime, nullable=True, comment="重置token过期时间")
    
    # 用户统计数据（可选，也可以单独建表）
    matches_count = Column(Integer, default=0, comment="比赛场次")
    goals_count = Column(Integer, default=0, comment="进球数")
    assists_count = Column(Integer, default=0, comment="助攻数")


# ==================== 首页相关 ====================
class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    desc = Column(String(500), nullable=True, comment="描述")
    image_url = Column(String(500), nullable=True, comment="图片URL")
    link_url = Column(String(500), nullable=True, comment="跳转链接")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


# ==================== 赛事相关 ====================
class MatchStatus(enum.Enum):
    UPCOMING = "upcoming"  # 即将开始
    ONGOING = "ongoing"    # 进行中
    FINISHED = "finished"  # 已结束


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="赛事名称")
    date = Column(DateTime, nullable=False, comment="比赛日期")
    time = Column(String(20), nullable=True, comment="比赛时间")
    location = Column(String(200), nullable=True, comment="比赛地点")
    status = Column(String(20), default="upcoming", comment="状态：upcoming/ongoing/finished")
    team_a = Column(String(100), nullable=False, comment="队伍A")
    team_b = Column(String(100), nullable=False, comment="队伍B")
    score_a = Column(Integer, default=0, comment="队伍A得分")
    score_b = Column(Integer, default=0, comment="队伍B得分")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class MatchRegistration(Base):
    __tablename__ = "match_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), nullable=False, comment="联系方式")
    event = Column(String(100), nullable=True, comment="参赛项目")
    status = Column(String(20), default="pending", comment="状态：pending/approved/rejected")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match", backref="registrations")
    user = relationship("User")


class MatchSchedule(Base):
    __tablename__ = "match_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    day = Column(String(10), nullable=False, comment="日期（日）")
    month = Column(String(10), nullable=False, comment="月份")
    team_a = Column(String(100), nullable=False, comment="队伍A")
    team_b = Column(String(100), nullable=False, comment="队伍B")
    time = Column(String(20), nullable=True, comment="比赛时间")
    score = Column(String(20), nullable=True, comment="比分")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match", backref="schedules")


class MatchPlayer(Base):
    __tablename__ = "match_players"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    name = Column(String(50), nullable=False, comment="球员姓名")
    position = Column(String(20), nullable=False, comment="位置")
    avatar = Column(String(500), nullable=True, comment="头像")
    votes = Column(Integer, default=0, comment="得票数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match", backref="players")


class MatchVote(Base):
    __tablename__ = "match_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    player_id = Column(Integer, ForeignKey("match_players.id"), nullable=False, comment="球员ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match")
    player = relationship("MatchPlayer")
    user = relationship("User")


class MatchReplay(Base):
    __tablename__ = "match_replays"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    title = Column(String(200), nullable=False, comment="标题")
    duration = Column(String(20), nullable=True, comment="时长")
    video_url = Column(String(500), nullable=True, comment="视频URL")
    time = Column(String(50), nullable=True, comment="时间段")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match", backref="replays")


class MatchCheer(Base):
    __tablename__ = "match_cheers"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, comment="赛事ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID（可选，匿名助威）")
    content = Column(String(500), nullable=False, comment="助威内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    match = relationship("Match", backref="cheers")
    user = relationship("User")


# ==================== 训练相关 ====================
class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    date = Column(DateTime, nullable=False, comment="训练日期")
    time = Column(String(20), nullable=False, comment="训练时间")
    title = Column(String(200), nullable=False, comment="训练标题")
    desc = Column(Text, nullable=True, comment="训练描述")
    completed = Column(Boolean, default=False, comment="是否完成")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    user = relationship("User", backref="training_plans")


class TrainingStat(Base):
    __tablename__ = "training_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    week_start = Column(DateTime, nullable=False, comment="周开始日期")
    total_days = Column(Integer, default=0, comment="训练天数")
    total_hours = Column(Float, default=0.0, comment="训练时长（小时）")
    completion_rate = Column(Float, default=0.0, comment="完成率")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    user = relationship("User", backref="training_stats")


class CoachPost(Base):
    __tablename__ = "coach_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发布者ID")
    content = Column(Text, nullable=False, comment="内容")
    likes = Column(Integer, default=0, comment="点赞数")
    comments = Column(Integer, default=0, comment="评论数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    user = relationship("User", backref="coach_posts")


# ==================== 社区相关 ====================
class CommunityTopic(Base):
    __tablename__ = "community_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="话题名称")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class CommunityPost(Base):
    __tablename__ = "community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发布者ID")
    topic_id = Column(Integer, ForeignKey("community_topics.id"), nullable=True, comment="话题ID")
    content = Column(Text, nullable=False, comment="内容")
    images = Column(Text, nullable=True, comment="图片URL列表（JSON格式）")
    likes = Column(Integer, default=0, comment="点赞数")
    comments = Column(Integer, default=0, comment="评论数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    user = relationship("User", backref="community_posts")
    topic = relationship("CommunityTopic", backref="posts")


class CommunityComment(Base):
    __tablename__ = "community_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False, comment="动态ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评论者ID")
    content = Column(Text, nullable=False, comment="评论内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    post = relationship("CommunityPost", backref="comment_list")
    user = relationship("User", backref="community_comments")


class CommunityLike(Base):
    __tablename__ = "community_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False, comment="动态ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="点赞者ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    post = relationship("CommunityPost")
    user = relationship("User")


# ==================== 技术学院相关 ====================
class AcademyCategory(Base):
    __tablename__ = "academy_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class AcademyVideo(Base):
    __tablename__ = "academy_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("academy_categories.id"), nullable=True, comment="分类ID")
    title = Column(String(200), nullable=False, comment="标题")
    cover = Column(String(500), nullable=True, comment="封面图")
    video_url = Column(String(500), nullable=True, comment="视频URL")
    duration = Column(String(20), nullable=True, comment="时长")
    desc = Column(Text, nullable=True, comment="描述")
    views = Column(Integer, default=0, comment="观看次数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    category = relationship("AcademyCategory", backref="videos")


class AcademyChallenge(Base):
    __tablename__ = "academy_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="挑战标题")
    desc = Column(Text, nullable=True, comment="挑战描述")
    is_daily = Column(Boolean, default=False, comment="是否每日挑战")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class AcademyChallengeRecord(Base):
    __tablename__ = "academy_challenge_records"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("academy_challenges.id"), nullable=False, comment="挑战ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    completed = Column(Boolean, default=False, comment="是否完成")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    challenge = relationship("AcademyChallenge")
    user = relationship("User")


class AcademyPersonalPlan(Base):
    __tablename__ = "academy_personal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID")
    title = Column(String(200), nullable=False, comment="计划标题")
    desc = Column(Text, nullable=True, comment="计划描述")
    progress = Column(Float, default=0.0, comment="完成进度（0-100）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    user = relationship("User", backref="personal_plan")


# ==================== 健康与营养相关 ====================
class HealthNutritionGuide(Base):
    __tablename__ = "health_nutrition_guides"
    
    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String(10), nullable=True, comment="图标")
    title = Column(String(200), nullable=False, comment="标题")
    desc = Column(String(500), nullable=True, comment="描述")
    content = Column(Text, nullable=True, comment="详细内容")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class HealthSleepData(Base):
    __tablename__ = "health_sleep_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    date = Column(DateTime, nullable=False, comment="日期")
    hours = Column(Float, nullable=False, comment="睡眠时长（小时）")
    quality = Column(String(20), nullable=True, comment="睡眠质量")
    goal_hours = Column(Float, default=9.0, comment="目标时长")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    user = relationship("User", backref="sleep_data")


class HealthInjuryPrevention(Base):
    __tablename__ = "health_injury_prevention"
    
    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String(10), nullable=True, comment="图标")
    title = Column(String(200), nullable=False, comment="标题")
    desc = Column(String(500), nullable=True, comment="描述")
    content = Column(Text, nullable=True, comment="详细内容")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class HealthInjuryCollection(Base):
    __tablename__ = "health_injury_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    injury_id = Column(Integer, ForeignKey("health_injury_prevention.id"), nullable=False, comment="内容ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    user = relationship("User")
    injury = relationship("HealthInjuryPrevention")


class HealthMonitorData(Base):
    __tablename__ = "health_monitor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    date = Column(DateTime, nullable=False, comment="日期")
    steps = Column(Integer, default=0, comment="步数")
    heart_rate = Column(Integer, nullable=True, comment="心率（bpm）")
    calories = Column(Integer, default=0, comment="消耗卡路里")
    device_id = Column(String(100), nullable=True, comment="设备ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    user = relationship("User", backref="monitor_data")


# ==================== 用户档案相关 ====================
class UserGrowthRecord(Base):
    __tablename__ = "user_growth_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    date = Column(DateTime, nullable=False, comment="日期")
    event = Column(String(500), nullable=False, comment="事件描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    user = relationship("User", backref="growth_records")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    skill_name = Column(String(50), nullable=False, comment="技能名称")
    score = Column(Integer, default=0, comment="技能评分（0-100）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    user = relationship("User", backref="skills")


# ==================== GPS 比赛录制 ====================
class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    started_at = Column(DateTime, nullable=False, comment="比赛开始时间")
    ended_at = Column(DateTime, nullable=True, comment="比赛结束时间")
    duration_seconds = Column(Integer, nullable=True, comment="比赛时长（秒）")
    total_distance_meters = Column(Float, nullable=True, comment="总跑动距离（米）")
    max_speed_kmh = Column(Float, nullable=True, comment="最高速度（km/h）")
    avg_speed_kmh = Column(Float, nullable=True, comment="平均速度（km/h）")
    goals = Column(Integer, default=0, comment="进球数")
    assists = Column(Integer, default=0, comment="助攻数")
    opponent = Column(String(100), nullable=True, comment="对手名称")
    score_own = Column(Integer, nullable=True, comment="己方得分")
    score_opp = Column(Integer, nullable=True, comment="对手得分")
    notes = Column(Text, nullable=True, comment="备注")
    status = Column(String(20), default="active", comment="状态: active/finished")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    user = relationship("User", backref="game_sessions")
    gps_points = relationship("GpsPoint", back_populates="session", cascade="all, delete-orphan")


class GpsPoint(Base):
    __tablename__ = "gps_points"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False, comment="比赛会话ID")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    speed_kmh = Column(Float, nullable=True, comment="当前速度（km/h）")
    altitude = Column(Float, nullable=True, comment="海拔（米）")
    recorded_at = Column(DateTime, nullable=False, comment="记录时间")

    session = relationship("GameSession", back_populates="gps_points")
