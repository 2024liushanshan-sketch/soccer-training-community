# 前端路径清单

## 所有页面路径（共12个）

1. `/pages/auth/login` - 登录页面
2. `/pages/auth/register` - 注册页面
3. `/pages/auth/forgot-password` - 忘记密码页面
4. `/pages/home/index` - 首页（Tab Bar）
5. `/pages/training/index` - 训练中心（Tab Bar）
6. `/pages/match/index` - 赛事中心（Tab Bar）
7. `/pages/profile/index` - 个人档案（Tab Bar）
8. `/pages/profile/settings` - 编辑资料页面
9. `/pages/community/index` - 球员社区（Tab Bar）
10. `/pages/academy/index` - 足球技术学院页面
11. `/pages/health/index` - 健康与营养页面
12. `/pages/match-experience/index` - 比赛日体验页面

## Tab Bar 页面（5个）

- `/pages/home/index` - 首页
- `/pages/training/index` - 训练
- `/pages/match/index` - 赛事
- `/pages/profile/index` - 我的
- `/pages/community/index` - 社区

## 页面间跳转关系

### 从登录页面 (`/pages/auth/login`)
- → `/pages/home/index` (登录成功后)
- → `/pages/auth/register` (点击注册)
- → `/pages/auth/forgot-password` (点击忘记密码)

### 从注册页面 (`/pages/auth/register`)
- → `/pages/auth/login` (注册成功后或返回登录)

### 从忘记密码页面 (`/pages/auth/forgot-password`)
- → `/pages/auth/login` (重置成功后或返回登录)

### 从首页 (`/pages/home/index`)
- → `/pages/training/index` (训练计划入口)
- → `/pages/match/index` (赛事报名入口，更多按钮)
- → `/pages/academy/index` (技术学院入口，更多按钮)
- → `/pages/health/index` (健康营养入口)
- → `/pages/profile/index` (数据档案入口)
- → `/pages/community/index` (社区入口)

### 从训练中心 (`/pages/training/index`)
- → `/pages/academy/index` (视频教程推荐)
- → `/pages/community/index` (教练社区推荐)

### 从赛事中心 (`/pages/match/index`)
- → `/pages/match-experience/index` (比赛直播入口)

### 从比赛日体验 (`/pages/match-experience/index`)
- → `/pages/match/index` (返回赛事中心，使用switchTab)

### 从个人档案 (`/pages/profile/index`)
- → `/pages/profile/settings` (点击头像进入设置)

### 从编辑资料 (`/pages/profile/settings`)
- → 返回上一页 (使用navigateBack)

### 从社区 (`/pages/community/index`)
- → `/pages/profile/index` (查看用户资料)

