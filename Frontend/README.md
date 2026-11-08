# ⚽ Soccer App - UniApp 极简文艺风

## 📱 页面结构

### 已实现的8个页面：

1. **🏠 主页 (pages/home/index.vue)**
   - 顶部Banner轮播（今日训练/比赛）
   - 6格快捷入口：训练计划、赛事报名、技术学院、健康营养、数据档案、社区
   - 热门赛事、推荐视频、足球知识卡片

2. **⚽ 训练中心 (pages/training/index.vue)**
   - 顶部Tabs：训练计划 / 数据分析 / 教练社区
   - 训练日历（可滑动）
   - 计划打卡卡片
   - 成绩统计
   - 推荐视频和挑战任务入口

3. **🏆 赛事中心 (pages/match/index.vue)**
   - 本地赛事信息列表
   - 在线报名功能
   - 赛程与战报
   - 比赛直播/MVP投票入口

4. **🎓 足球技术学院 (pages/academy/index.vue)**
   - 视频教学区（搜索、分类）
   - 挑战模式入口
   - 个性化训练计划

5. **💪 健康与营养 (pages/health/index.vue)**
   - 青少年运动营养指南
   - 休息与睡眠监测
   - 运动损伤预防与康复
   - 健康监测（手环数据）

6. **👤 个人档案 (pages/profile/index.vue)**
   - 个人信息卡
   - 成长记录时间轴
   - 数据统计图表
   - 导出/分享功能

7. **💬 球员社区 (pages/community/index.vue)**
   - 话题区（#训练心得 #赛事讨论）
   - 附近球友推荐
   - 动态卡片流（点赞、评论）

8. **📺 比赛体验 (pages/match-experience/index.vue)**
   - 实时比分与直播
   - MVP投票
   - 比赛回放
   - 线上助威墙

## 🎨 设计特点

- **极简文艺风格**：浅灰背景、圆角白色卡片
- **统一配色**：主色调 #3CB371（绿色），渐变背景 #667eea → #764ba2
- **流畅动效**：卡片hover微缩放、点赞动画、平滑过渡
- **无衬线字体**：系统默认字体栈

## 📋 底部导航栏

5个Tab：
- 🏠 首页 → pages/home/index
- ⚽ 训练 → pages/training/index
- 🏆 赛事 → pages/match/index
- 👤 我的 → pages/profile/index
- 💬 社区 → pages/community/index

## ⚠️ 注意事项

### Tab Bar 图标

需要在 `static/icons/` 目录下添加以下图标文件：
- `home.png` / `home_active.png`
- `train.png` / `train_active.png`
- `match.png` / `match_active.png`
- `user.png` / `user_active.png`
- `chat.png` / `chat_active.png`

如果暂时没有图标，可以：
1. 使用占位图片
2. 或者修改 `pages.json` 中的 tabBar 配置，移除 iconPath 和 selectedIconPath

### 图片资源

部分页面引用了图片资源（如头像、视频封面等），需要：
- 在 `static/` 目录下添加相应的图片文件
- 或修改代码中的图片路径为实际存在的资源

## 🚀 运行项目

1. 使用 HBuilderX 打开项目
2. 选择运行到浏览器/微信小程序/App
3. 或使用命令行：
   ```bash
   npm run dev:h5        # H5
   npm run dev:mp-weixin # 微信小程序
   ```

## 📝 页面跳转规则

- 主页 → 各功能模块（通过快捷入口）
- 训练中心 → 技术学院、社区
- 赛事中心 → 比赛体验
- 社区 → 个人档案
- 所有页面可通过底部Tab导航切换

## 🎯 后续开发建议

1. 添加后端API接口
2. 实现用户登录/注册
3. 完善数据持久化
4. 添加更多交互动效
5. 优化移动端体验
6. 集成图表库（如 ECharts）用于数据可视化

