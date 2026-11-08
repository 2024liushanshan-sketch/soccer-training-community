# API接口设计文档

## 一、认证相关 API (`/api/auth`)
**用途：用户注册、登录、忘记密码等认证功能**

1. `POST /api/auth/register` - 用户注册
2. `POST /api/auth/login` - 用户登录
3. `POST /api/auth/login-json` - 用户登录（JSON格式）
4. `GET /api/auth/me` - 获取当前用户信息
5. `POST /api/auth/forgot-password` - 忘记密码（发送重置邮件）
6. `POST /api/auth/reset-password` - 重置密码

## 二、个人资料相关 API (`/api/profile`)
**用途：用户个人资料管理**

1. `GET /api/profile/me` - 获取个人资料
2. `PUT /api/profile/me` - 更新个人资料
3. `POST /api/profile/avatar` - 上传头像
4. `GET /api/profile/avatar/{filename}` - 获取头像文件

## 三、首页相关 API (`/api/home`)
**用途：首页Banner、热门赛事、推荐视频、足球知识等**

1. `GET /api/home/banners` - 获取首页Banner列表
2. `GET /api/home/hot-matches` - 获取热门赛事列表
3. `GET /api/home/recommended-videos` - 获取推荐视频列表
4. `GET /api/home/knowledge` - 获取足球知识卡片

## 四、训练中心相关 API (`/api/training`)
**用途：训练计划、数据分析、教练社区**

1. `GET /api/training/plans` - 获取训练计划列表（支持日期筛选）
2. `POST /api/training/plans` - 创建训练计划
3. `PUT /api/training/plans/{plan_id}` - 更新训练计划
4. `DELETE /api/training/plans/{plan_id}` - 删除训练计划
5. `POST /api/training/plans/{plan_id}/check` - 训练计划打卡
6. `GET /api/training/stats` - 获取训练统计数据（本周训练天数、时长、完成率等）
7. `GET /api/training/analysis` - 获取数据分析数据
8. `GET /api/training/coach-posts` - 获取教练社区动态列表
9. `POST /api/training/coach-posts` - 发布教练社区动态
10. `GET /api/training/coach-posts/{post_id}` - 获取教练社区动态详情

## 五、赛事中心相关 API (`/api/match`)
**用途：本地赛事、在线报名、赛程战报、MVP投票**

1. `GET /api/match/local` - 获取本地赛事列表
2. `GET /api/match/{match_id}` - 获取赛事详情
3. `GET /api/match/registrations` - 获取在线报名信息
4. `POST /api/match/registrations` - 提交赛事报名
5. `GET /api/match/schedules` - 获取赛程与战报列表
6. `GET /api/match/{match_id}/schedules` - 获取指定赛事的赛程
7. `POST /api/match/{match_id}/schedules` - 创建赛程
8. `PUT /api/match/schedules/{schedule_id}` - 更新赛程（更新比分等）
9. `GET /api/match/{match_id}/live` - 获取比赛直播数据（实时比分、状态等）
10. `GET /api/match/{match_id}/players` - 获取比赛球员列表
11. `POST /api/match/{match_id}/players/{player_id}/vote` - MVP投票
12. `GET /api/match/{match_id}/replays` - 获取比赛回放列表
13. `GET /api/match/{match_id}/cheers` - 获取助威墙消息列表
14. `POST /api/match/{match_id}/cheers` - 发送助威消息

## 六、社区相关 API (`/api/community`)
**用途：话题、附近球友、动态、评论、点赞**

1. `GET /api/community/topics` - 获取话题列表
2. `GET /api/community/friends/nearby` - 获取附近球友列表（支持距离筛选）
3. `GET /api/community/posts` - 获取动态列表（支持话题筛选、分页）
4. `POST /api/community/posts` - 发布动态
5. `GET /api/community/posts/{post_id}` - 获取动态详情
6. `PUT /api/community/posts/{post_id}` - 更新动态
7. `DELETE /api/community/posts/{post_id}` - 删除动态
8. `POST /api/community/posts/{post_id}/like` - 点赞/取消点赞动态
9. `GET /api/community/posts/{post_id}/comments` - 获取动态评论列表
10. `POST /api/community/posts/{post_id}/comments` - 发表评论
11. `DELETE /api/community/comments/{comment_id}` - 删除评论
12. `POST /api/community/posts/{post_id}/share` - 分享动态

## 七、技术学院相关 API (`/api/academy`)
**用途：视频教程、分类、挑战任务、个性化训练计划**

1. `GET /api/academy/categories` - 获取视频分类列表
2. `GET /api/academy/videos` - 获取视频列表（支持分类、搜索、分页）
3. `GET /api/academy/videos/{video_id}` - 获取视频详情
4. `POST /api/academy/videos/{video_id}/view` - 记录视频观看（增加观看次数）
5. `GET /api/academy/challenges` - 获取挑战任务列表
6. `GET /api/academy/challenges/daily` - 获取每日挑战任务
7. `POST /api/academy/challenges/{challenge_id}/complete` - 完成挑战任务
8. `GET /api/academy/personal-plan` - 获取个性化训练计划
9. `POST /api/academy/personal-plan` - 创建/更新个性化训练计划

## 八、健康与营养相关 API (`/api/health`)
**用途：营养指南、睡眠监测、损伤预防、健康数据**

1. `GET /api/health/nutrition-guides` - 获取营养指南列表
2. `GET /api/health/nutrition-guides/{guide_id}` - 获取营养指南详情
3. `GET /api/health/sleep` - 获取睡眠监测数据
4. `POST /api/health/sleep` - 记录睡眠数据
5. `GET /api/health/sleep-tips` - 获取睡眠小贴士
6. `GET /api/health/injury-prevention` - 获取运动损伤预防与康复内容列表
7. `GET /api/health/injury-prevention/{item_id}` - 获取运动损伤预防与康复详情
8. `POST /api/health/injury-prevention/{item_id}/collect` - 收藏/取消收藏
9. `GET /api/health/monitor` - 获取健康监测数据（步数、心率、卡路里等）
10. `POST /api/health/monitor` - 上传健康监测数据
11. `POST /api/health/device/connect` - 连接智能设备


