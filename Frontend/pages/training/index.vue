<template>
	<view class="training-page">
		<!-- 顶部Tabs -->
		<view class="tabs-container">
			<view class="tab-item" :class="{ active: currentTab === 0 }" @click="switchTab(0)">
				<text>训练计划</text>
			</view>
			<view class="tab-item" :class="{ active: currentTab === 1 }" @click="switchTab(1)">
				<text>数据分析</text>
			</view>
			<view class="tab-item" :class="{ active: currentTab === 2 }" @click="switchTab(2)">
				<text>教练社区</text>
			</view>
		</view>

		<!-- 训练计划内容 -->
		<view v-if="currentTab === 0" class="tab-content">
			<!-- 训练日历 -->
			<view class="calendar-card">
				<scroll-view class="calendar-scroll" scroll-x>
					<view class="calendar-item" v-for="(day, index) in calendarDays" :key="index" 
						:class="{ today: day.isToday, selected: day.isSelected }" @click="selectDay(index)">
						<text class="day-name">{{ day.name }}</text>
						<text class="day-date">{{ day.date }}</text>
					</view>
				</scroll-view>
			</view>

			<!-- 计划打卡卡片 -->
			<view class="plan-card" v-for="plan in trainingPlans" :key="plan.id">
				<view class="plan-header">
					<text class="plan-time">{{ plan.time }}</text>
					<text class="plan-status" :class="{ completed: plan.completed }">
						{{ plan.completed ? '已完成' : '未完成' }}
					</text>
				</view>
				<text class="plan-title">{{ plan.title }}</text>
				<text class="plan-desc">{{ plan.desc }}</text>
				<button class="check-btn" :class="{ completed: plan.completed }" 
					@click="toggleCheck(plan.id)">
					{{ plan.completed ? '✓ 已完成' : '完成打卡' }}
				</button>
			</view>

			<!-- 成绩统计 -->
			<view class="stats-card">
				<text class="stats-title">本周训练统计</text>
				<view class="stats-grid">
					<view class="stats-item">
						<text class="stats-value">{{ stats.totalDays }}</text>
						<text class="stats-label">训练天数</text>
					</view>
					<view class="stats-item">
						<text class="stats-value">{{ stats.totalHours }}</text>
						<text class="stats-label">训练时长</text>
					</view>
					<view class="stats-item">
						<text class="stats-value">{{ stats.completionRate }}%</text>
						<text class="stats-label">完成率</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 数据分析内容 -->
		<view v-if="currentTab === 1" class="tab-content">
			<view class="data-card" v-for="data in dataAnalysis" :key="data.id">
				<text class="data-title">{{ data.title }}</text>
				<text class="data-value">{{ data.value }}</text>
				<text class="data-desc">{{ data.desc }}</text>
			</view>
		</view>

		<!-- 教练社区内容 -->
		<view v-if="currentTab === 2" class="tab-content">
			<view class="community-card" v-for="post in coachPosts" :key="post.id">
				<view class="post-header">
					<text class="post-author">{{ post.author }}</text>
					<text class="post-time">{{ post.time }}</text>
				</view>
				<text class="post-content">{{ post.content }}</text>
				<view class="post-actions">
					<text class="action-item">👍 {{ post.likes }}</text>
					<text class="action-item">💬 {{ post.comments }}</text>
				</view>
			</view>
		</view>

		<!-- 推荐视频和挑战任务 -->
		<view class="recommend-section">
			<view class="recommend-card" @click="navigateTo('/pages/academy/index')">
				<text class="recommend-title">📹 视频教程</text>
				<text class="recommend-desc">学习专业训练技巧</text>
			</view>
			<view class="recommend-card" @click="navigateTo('/pages/community/index')">
				<text class="recommend-title">💬 教练社区</text>
				<text class="recommend-desc">与教练交流经验</text>
			</view>
		</view>
	</view>
</template>

<script>
import { trainingAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			currentTab: 0,
			calendarDays: [],
			trainingPlans: [],
			stats: {
				totalDays: 0,
				totalHours: 0,
				completionRate: 0
			},
			dataAnalysis: [],
			coachPosts: [],
			loading: false,
			selectedDate: null
		}
	},
	onLoad() {
		this.initCalendar()
		this.loadData()
	},
	methods: {
		isLoggedIn() {
			return !!uni.getStorageSync('token')
		},
		initCalendar() {
			// 动态生成本周日历
			const today = new Date()
			const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
			const calendarDays = []
			
			// 获取本周一的日期
			const dayOfWeek = today.getDay()
			const monday = new Date(today)
			monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))
			
			let selectedIndex = 0
			for (let i = 0; i < 7; i++) {
				const date = new Date(monday)
				date.setDate(monday.getDate() + i)
				const isToday = date.toDateString() === today.toDateString()
				// 默认选中今天
				if (isToday) {
					selectedIndex = i
				}
				
				calendarDays.push({
					name: days[date.getDay()],
					date: date.getDate().toString(),
					isToday: isToday,
					isSelected: isToday, // 默认选中今天
					fullDate: date
				})
			}
			
			this.calendarDays = calendarDays
			this.selectedDate = today.toISOString().split('T')[0]
		},
		async loadData() {
			// 游客模式：允许访问所有数据，未登录时返回空数据或示例数据
			this.loading = true
			try {
				// 根据当前tab加载不同数据
				if (this.currentTab === 0) {
					// 加载训练计划和统计，单个请求失败不影响其他请求
					const [plans, stats] = await Promise.all([
						trainingAPI.getPlans(this.selectedDate).catch(() => []),
						trainingAPI.getStats().catch(() => null)
					])
					this.trainingPlans = plans || []
					if (stats) {
						this.stats = {
							totalDays: stats.total_days || 0,
							totalHours: stats.total_hours || 0,
							completionRate: Math.round(stats.completion_rate || 0)
						}
					}
				} else if (this.currentTab === 1) {
					// 加载数据分析
					const analysis = await trainingAPI.getAnalysis()
					this.dataAnalysis = analysis || []
				} else if (this.currentTab === 2) {
					// 加载教练社区动态
					const posts = await trainingAPI.getCoachPosts()
					this.coachPosts = posts || []
				}
			} catch (error) {
				console.error('加载数据失败:', error)
				// 如果是401错误，不显示错误提示（会在request中自动跳转登录）
				if (error.statusCode !== 401) {
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				}
			} finally {
				this.loading = false
			}
		},
		switchTab(index) {
			this.currentTab = index
			this.loadData()
		},
		selectDay(index) {
			// 检查索引有效性
			if (!Array.isArray(this.calendarDays) || typeof index !== 'number' || index < 0 || index >= this.calendarDays.length) {
				return
			}
			
			// 确保只有一个日期被选中 - 先重置所有选中状态
			for (let i = 0; i < this.calendarDays.length; i++) {
				if (this.calendarDays[i]) {
					this.$set(this.calendarDays[i], 'isSelected', i === index)
				}
			}
			// 更新选中的日期并重新加载数据
			const selectedDay = this.calendarDays[index]
			if (selectedDay && selectedDay.fullDate) {
				try {
					this.selectedDate = selectedDay.fullDate.toISOString().split('T')[0]
					this.loadData()
				} catch (e) {
					console.error('日期格式化失败:', e)
				}
			}
		},
		async toggleCheck(id) {
			if (!id) {
				uni.showToast({
					title: '计划ID无效',
					icon: 'none'
				})
				return
			}
			
			try {
				const updatedPlan = await trainingAPI.checkPlan(id)
				// 更新本地数据
				if (!Array.isArray(this.trainingPlans)) {
					this.trainingPlans = []
				}
				const plan = this.trainingPlans.find(p => p && p.id === id)
				if (plan && updatedPlan) {
					plan.completed = updatedPlan.completed !== undefined ? updatedPlan.completed : !plan.completed
				}
				// 重新加载统计
				const stats = await trainingAPI.getStats()
				if (stats) {
					this.stats = {
						totalDays: stats.total_days || 0,
						totalHours: stats.total_hours || 0,
						completionRate: Math.round(stats.completion_rate || 0)
					}
				}
			} catch (error) {
				console.error('打卡失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
				} else {
					uni.showToast({
						title: error.message || '操作失败',
						icon: 'none'
					})
				}
			}
		},
		navigateTo(path) {
			uni.navigateTo({
				url: path
			})
		}
	}
}
</script>

<style scoped>
.training-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.tabs-container {
	display: flex;
	background: #FFFFFF;
	padding: 0 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 30rpx 0;
	font-size: 28rpx;
	color: #999999;
	position: relative;
}

.tab-item.active {
	color: #3CB371;
	font-weight: 600;
}

.tab-item.active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 50%;
	transform: translateX(-50%);
	width: 60rpx;
	height: 4rpx;
	background: #3CB371;
	border-radius: 2rpx;
}

.tab-content {
	padding: 30rpx 20rpx;
}

.calendar-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.calendar-scroll {
	white-space: nowrap;
}

.calendar-item {
	display: inline-block;
	width: 100rpx;
	padding: 20rpx 10rpx;
	margin-right: 20rpx;
	text-align: center;
	border-radius: 12rpx;
	background: #F5F5F5;
	transition: all 0.3s;
}

.calendar-item.today:not(.selected) {
	border: 2rpx solid #3CB371;
}

.calendar-item.selected {
	background: #3CB371;
	box-shadow: 0 4rpx 12rpx rgba(60, 179, 113, 0.3);
}

.calendar-item.selected .day-name,
.calendar-item.selected .day-date {
	color: #FFFFFF;
}

.day-name {
	display: block;
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 5rpx;
}

.day-date {
	display: block;
	font-size: 28rpx;
	font-weight: 600;
	color: #333333;
}

.plan-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	transition: transform 0.2s, box-shadow 0.2s;
}

.plan-card:active {
	transform: translateY(-2rpx);
	box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.12);
}

.plan-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15rpx;
}

.plan-time {
	font-size: 28rpx;
	font-weight: 600;
	color: #333333;
}

.plan-status {
	font-size: 24rpx;
	color: #999999;
}

.plan-status.completed {
	color: #3CB371;
}

.plan-title {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
}

.plan-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 20rpx;
}

.check-btn {
	width: 100%;
	padding: 20rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.check-btn.completed {
	background: #E8F5E9;
	color: #3CB371;
}

.stats-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-top: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.stats-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 30rpx;
}

.stats-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
}

.stats-item {
	text-align: center;
}

.stats-value {
	display: block;
	font-size: 40rpx;
	font-weight: 600;
	color: #3CB371;
	margin-bottom: 10rpx;
}

.stats-label {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.data-card,
.community-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.data-title {
	display: block;
	font-size: 28rpx;
	color: #666666;
	margin-bottom: 10rpx;
}

.data-value {
	display: block;
	font-size: 48rpx;
	font-weight: 600;
	color: #3CB371;
	margin-bottom: 10rpx;
}

.data-desc {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.post-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 15rpx;
}

.post-author {
	font-size: 28rpx;
	font-weight: 600;
	color: #333333;
}

.post-time {
	font-size: 24rpx;
	color: #999999;
}

.post-content {
	display: block;
	font-size: 28rpx;
	color: #666666;
	line-height: 1.6;
	margin-bottom: 15rpx;
}

.post-actions {
	display: flex;
	gap: 30rpx;
}

.action-item {
	font-size: 24rpx;
	color: #999999;
}

.recommend-section {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
	padding: 30rpx 20rpx;
}

.recommend-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.recommend-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.recommend-desc {
	display: block;
	font-size: 24rpx;
	color: #999999;
}
</style>
