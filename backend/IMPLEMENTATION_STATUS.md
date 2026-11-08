# 后端实现状态文档

## 已完成的工作

### 1. API接口设计 ✅
- 已创建 `API_DESIGN.md` 文档，列出了所有需要的API接口清单
- 接口按功能模块分类：认证、个人资料、首页、训练、赛事、社区、技术学院、健康营养

### 2. 数据库表结构设计 ✅
- 已创建完整的数据库模型文件 `app/models.py`
- 包含以下表：
  - `users` - 用户表（已存在，已扩展）
  - `banners` - 首页Banner
  - `knowledge` - 足球知识
  - `matches` - 赛事
  - `match_registrations` - 赛事报名
  - `match_schedules` - 赛程
  - `match_players` - 比赛球员
  - `match_votes` - MVP投票
  - `match_replays` - 比赛回放
  - `match_cheers` - 助威墙
  - `training_plans` - 训练计划
  - `training_stats` - 训练统计
  - `coach_posts` - 教练社区动态
  - `community_topics` - 社区话题
  - `community_posts` - 社区动态
  - `community_comments` - 评论
  - `community_likes` - 点赞
  - `academy_categories` - 视频分类
  - `academy_videos` - 视频
  - `academy_challenges` - 挑战任务
  - `academy_challenge_records` - 挑战记录
  - `academy_personal_plans` - 个性化训练计划
  - `health_nutrition_guides` - 营养指南
  - `health_sleep_data` - 睡眠数据
  - `health_injury_prevention` - 损伤预防内容
  - `health_injury_collections` - 损伤预防收藏
  - `health_monitor_data` - 健康监测数据

### 3. Pydantic模型定义 ✅
- 已创建 `app/schemas_extended.py`，包含所有新增的Pydantic模型
- 覆盖了所有API需要的请求和响应模型

### 4. 部分路由实现 ✅
- ✅ 认证相关路由 (`app/routers/auth.py`) - 已完成
- ✅ 个人资料路由 (`app/routers/profile.py`) - 已完成
- ✅ 首页路由 (`app/routers/home.py`) - 已创建基础框架

## 待完成的工作

### 1. 路由实现（需要创建以下路由文件）

#### 训练中心路由 (`app/routers/training.py`)
- [ ] GET /api/training/plans - 获取训练计划列表
- [ ] POST /api/training/plans - 创建训练计划
- [ ] PUT /api/training/plans/{plan_id} - 更新训练计划
- [ ] DELETE /api/training/plans/{plan_id} - 删除训练计划
- [ ] POST /api/training/plans/{plan_id}/check - 训练计划打卡
- [ ] GET /api/training/stats - 获取训练统计数据
- [ ] GET /api/training/analysis - 获取数据分析数据
- [ ] GET /api/training/coach-posts - 获取教练社区动态列表
- [ ] POST /api/training/coach-posts - 发布教练社区动态

#### 赛事中心路由 (`app/routers/match.py`)
- [ ] GET /api/match/local - 获取本地赛事列表
- [ ] GET /api/match/{match_id} - 获取赛事详情
- [ ] GET /api/match/registrations - 获取在线报名信息
- [ ] POST /api/match/registrations - 提交赛事报名
- [ ] GET /api/match/schedules - 获取赛程与战报列表
- [ ] GET /api/match/{match_id}/live - 获取比赛直播数据
- [ ] GET /api/match/{match_id}/players - 获取比赛球员列表
- [ ] POST /api/match/{match_id}/players/{player_id}/vote - MVP投票
- [ ] GET /api/match/{match_id}/replays - 获取比赛回放列表
- [ ] GET /api/match/{match_id}/cheers - 获取助威墙消息列表
- [ ] POST /api/match/{match_id}/cheers - 发送助威消息

#### 社区路由 (`app/routers/community.py`)
- [ ] GET /api/community/topics - 获取话题列表
- [ ] GET /api/community/friends/nearby - 获取附近球友列表
- [ ] GET /api/community/posts - 获取动态列表
- [ ] POST /api/community/posts - 发布动态
- [ ] GET /api/community/posts/{post_id} - 获取动态详情
- [ ] POST /api/community/posts/{post_id}/like - 点赞/取消点赞
- [ ] GET /api/community/posts/{post_id}/comments - 获取评论列表
- [ ] POST /api/community/posts/{post_id}/comments - 发表评论

#### 技术学院路由 (`app/routers/academy.py`)
- [ ] GET /api/academy/categories - 获取视频分类列表
- [ ] GET /api/academy/videos - 获取视频列表
- [ ] GET /api/academy/videos/{video_id} - 获取视频详情
- [ ] POST /api/academy/videos/{video_id}/view - 记录视频观看
- [ ] GET /api/academy/challenges/daily - 获取每日挑战任务
- [ ] POST /api/academy/challenges/{challenge_id}/complete - 完成挑战任务
- [ ] GET /api/academy/personal-plan - 获取个性化训练计划
- [ ] POST /api/academy/personal-plan - 创建/更新个性化训练计划

#### 健康与营养路由 (`app/routers/health.py`)
- [ ] GET /api/health/nutrition-guides - 获取营养指南列表
- [ ] GET /api/health/nutrition-guides/{guide_id} - 获取营养指南详情
- [ ] GET /api/health/sleep - 获取睡眠监测数据
- [ ] POST /api/health/sleep - 记录睡眠数据
- [ ] GET /api/health/injury-prevention - 获取运动损伤预防内容列表
- [ ] POST /api/health/injury-prevention/{item_id}/collect - 收藏/取消收藏
- [ ] GET /api/health/monitor - 获取健康监测数据
- [ ] POST /api/health/monitor - 上传健康监测数据

### 2. CRUD操作（需要创建或扩展 `app/crud.py`）
- [ ] 首页相关CRUD
- [ ] 训练相关CRUD
- [ ] 赛事相关CRUD
- [ ] 社区相关CRUD
- [ ] 技术学院相关CRUD
- [ ] 健康相关CRUD

### 3. 数据库初始化数据
- [ ] 创建初始数据脚本（Banner、Knowledge、Topics、Categories等）
- [ ] 添加示例数据

### 4. 前端代码修改
- [ ] 修改 `Frontend/utils/api.js`，添加所有新的API调用
- [ ] 修改 `Frontend/pages/home/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/training/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/match/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/community/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/academy/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/health/index.vue`，接入后端API
- [ ] 修改 `Frontend/pages/match-experience/index.vue`，接入后端API

## 下一步计划

1. **优先完成核心路由**：训练、赛事、社区（这些是主要功能）
2. **实现CRUD操作**：为每个模块创建CRUD函数
3. **添加初始数据**：创建数据库初始化脚本
4. **前端接入**：逐步修改前端页面，接入后端API
5. **测试验证**：确保前后端联动正常

## 注意事项

1. 所有路由都需要考虑用户认证（使用 `get_current_user`）
2. 需要处理分页、筛选、排序等功能
3. 需要处理文件上传（头像、图片、视频等）
4. 需要处理地理位置计算（附近球友功能）
5. 需要处理相对时间显示（如"2小时前"）
6. 需要处理点赞、收藏等状态的判断（当前用户是否已点赞/收藏）


