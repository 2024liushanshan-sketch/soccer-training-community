<template>
	<view class="profile-page">
		<!-- 个人信息卡 -->
		<view class="profile-card">
			<view class="avatar-section" @click="goToSettings">
				<image class="avatar" :src="avatarUrl" mode="aspectFill" />
				<text class="edit-icon">✏️</text>
			</view>
			<text class="user-name">{{ userInfo.name }}</text>
			<text class="user-desc">{{ userInfo.desc }}</text>
			<view class="user-stats">
				<view class="stat-item">
					<text class="stat-value">{{ userInfo.stats.matches }}</text>
					<text class="stat-label">比赛场次</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ userInfo.stats.goals }}</text>
					<text class="stat-label">进球数</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ userInfo.stats.assists }}</text>
					<text class="stat-label">助攻数</text>
				</view>
			</view>
		</view>

		<!-- 成长记录时间轴 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">成长记录</text>
				<text class="section-more" @click="showGrowthDetail">查看全部 ></text>
			</view>
			<view class="timeline">
				<view class="timeline-item" v-for="(record, index) in growthRecords" :key="index">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="timeline-date">{{ record.date }}</text>
						<text class="timeline-event">{{ record.event }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 数据统计 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">数据统计</text>
			</view>
			<view class="stats-container">
				<view class="chart-card">
					<text class="chart-title">训练时长趋势</text>
					<view class="chart-wrapper">
						<!-- 使用SVG绘制曲线图 -->
						<view class="chart-container">
							<view class="chart-y-axis">
								<text class="y-label" v-for="(label, index) in yAxisLabels" :key="index">{{ label }}h</text>
							</view>
							<view class="chart-main">
								<svg class="chart-svg" :viewBox="`0 0 ${chartViewBox.width} ${chartViewBox.height}`" preserveAspectRatio="xMidYMid meet">
									<!-- 网格线 -->
									<line 
										v-for="(y, index) in gridLines" 
										:key="'grid-' + index"
										:x1="0" 
										:y1="y" 
										:x2="chartViewBox.width" 
										:y2="y" 
										stroke="#F5F5F5" 
										stroke-width="1"
									/>
									<!-- 填充区域 -->
									<path 
										:d="chartAreaPath" 
										fill="url(#chartGradient)" 
										opacity="0.3"
									/>
									<!-- 曲线 -->
									<path 
										:d="chartLinePath" 
										fill="none" 
										stroke="#3CB371" 
										stroke-width="3" 
										stroke-linecap="round" 
										stroke-linejoin="round"
									/>
									<!-- 数据点 -->
									<circle 
										v-for="(point, index) in chartPoints" 
										:key="'point-' + index"
										:cx="point.x" 
										:cy="point.y" 
										r="6" 
										fill="#3CB371"
									/>
									<circle 
										v-for="(point, index) in chartPoints" 
										:key="'point-bg-' + index"
										:cx="point.x" 
										:cy="point.y" 
										r="10" 
										fill="rgba(60, 179, 113, 0.15)"
									/>
									<!-- 渐变定义 -->
									<defs>
										<linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
											<stop offset="0%" style="stop-color:#3CB371;stop-opacity:0.3" />
											<stop offset="100%" style="stop-color:#3CB371;stop-opacity:0.05" />
										</linearGradient>
									</defs>
								</svg>
								<!-- 数据标签 -->
								<view class="chart-labels">
									<view class="chart-label-item" v-for="(point, index) in chartPoints" :key="'label-' + index" 
										:style="{ 
											left: (point.x / chartViewBox.width * 100) + '%',
											top: (point.y / chartViewBox.height * 100) + '%'
										}">
										<text class="label-value">{{ point.value }}h</text>
									</view>
									<view class="chart-x-labels">
										<view class="x-label-item" v-for="(point, index) in chartPoints" :key="'xlabel-' + index" 
											:style="{ left: (point.x / chartViewBox.width * 100) + '%' }">
											<text class="label-week">{{ point.week }}</text>
										</view>
									</view>
								</view>
							</view>
						</view>
						<view class="chart-info">
							<view class="info-item">
								<text class="info-label">本周</text>
								<text class="info-value">{{ (weeklyData && weeklyData.length > 0) ? (weeklyData[weeklyData.length - 1]?.hours || 0) : 0 }}小时</text>
							</view>
							<view class="info-item">
								<text class="info-label">较上周</text>
								<text class="info-value" :class="{ increase: weeklyChange >= 0, decrease: weeklyChange < 0 }">
									{{ weeklyChange >= 0 ? '↑' : '↓' }} {{ Math.abs(weeklyChange) }}小时
								</text>
							</view>
						</view>
					</view>
				</view>
				<view class="chart-card">
					<text class="chart-title">技能评分</text>
					<view class="skill-list">
						<view class="skill-item" v-for="skill in skills" :key="skill.name">
							<text class="skill-name">{{ skill.name }}</text>
							<view class="skill-bar">
								<view class="skill-fill" :style="{ width: skill.score + '%' }"></view>
							</view>
							<text class="skill-score">{{ skill.score }}分</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 导出/分享 -->
		<view class="section">
			<view class="action-buttons">
				<button class="action-btn export" @click="exportProfile">导出档案</button>
				<button class="action-btn share" @click="shareProfile">分享档案</button>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="section">
			<button class="logout-btn" @click="handleLogout">退出登录</button>
		</view>
	</view>
</template>

<script>
import { authAPI, profileAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			userInfo: {
				name: '',
				desc: '',
				stats: {
					matches: 0,
					goals: 0,
					assists: 0
				}
			},
			avatarUrl: '/static/avatar.png',
			growthRecords: [],
			stats: {
				trainingHours: 0
			},
			skills: [],
			weeklyData: [],
			weeklyChange: 0,
			loading: false
		}
	},
	computed: {
		// 计算图表数据
		chartViewBox() {
			return { width: 600, height: 300 }
		},
		chartPoints() {
			if (!this.weeklyData || this.weeklyData.length === 0) return []
			
			const padding = { top: 40, right: 40, bottom: 50, left: 50 }
			const chartWidth = this.chartViewBox.width - padding.left - padding.right
			const chartHeight = this.chartViewBox.height - padding.top - padding.bottom
			
			const hours = this.weeklyData.map(item => item?.hours || 0).filter(h => typeof h === 'number')
			if (hours.length === 0) return []
			
			const maxHours = Math.max(...hours) + 2
			const minHours = Math.max(0, Math.min(...hours) - 2)
			const range = maxHours - minHours || 1
			
			const pointCount = this.weeklyData.length
			const pointGap = pointCount > 1 ? chartWidth / (pointCount - 1) : 0
			
			return this.weeklyData.map((item, index) => {
				const itemHours = item?.hours || 0
				const x = padding.left + pointGap * index
				const y = padding.top + chartHeight - ((itemHours - minHours) / range) * chartHeight
				let weekLabel = item?.week || ''
				if (weekLabel && typeof weekLabel === 'string' && weekLabel.includes('周前')) {
					weekLabel = weekLabel.replace('周前', '')
				}
				return { 
					x, 
					y, 
					value: itemHours, 
					week: weekLabel 
				}
			})
		},
		chartLinePath() {
			if (this.chartPoints.length === 0) return ''
			
			let path = `M ${this.chartPoints[0].x} ${this.chartPoints[0].y}`
			
			for (let i = 1; i < this.chartPoints.length; i++) {
				const prevPoint = this.chartPoints[i - 1]
				const currentPoint = this.chartPoints[i]
				const cp1x = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5
				const cp1y = prevPoint.y
				const cp2x = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5
				const cp2y = currentPoint.y
				path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${currentPoint.x} ${currentPoint.y}`
			}
			
			return path
		},
		chartAreaPath() {
			if (this.chartPoints.length === 0) return ''
			
			const padding = { top: 40, bottom: 50 }
			const chartHeight = this.chartViewBox.height - padding.top - padding.bottom
			const baseY = padding.top + chartHeight
			
			let path = `M ${this.chartPoints[0].x} ${baseY}`
			path += ` L ${this.chartPoints[0].x} ${this.chartPoints[0].y}`
			
			for (let i = 1; i < this.chartPoints.length; i++) {
				const prevPoint = this.chartPoints[i - 1]
				const currentPoint = this.chartPoints[i]
				const cp1x = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5
				const cp1y = prevPoint.y
				const cp2x = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5
				const cp2y = currentPoint.y
				path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${currentPoint.x} ${currentPoint.y}`
			}
			
			path += ` L ${this.chartPoints[this.chartPoints.length - 1].x} ${baseY} Z`
			
			return path
		},
		gridLines() {
			const padding = { top: 40, bottom: 50 }
			const chartHeight = this.chartViewBox.height - padding.top - padding.bottom
			const lines = []
			for (let i = 0; i <= 4; i++) {
				lines.push(padding.top + (chartHeight / 4) * i)
			}
			return lines
		},
		yAxisLabels() {
			if (!this.weeklyData || this.weeklyData.length === 0) return []
			const hours = this.weeklyData.map(item => item?.hours || 0).filter(h => typeof h === 'number')
			if (hours.length === 0) return [0, 0, 0, 0, 0]
			const maxHours = Math.max(...hours) + 2
			const minHours = Math.max(0, Math.min(...hours) - 2)
			const range = maxHours - minHours || 1
			const labels = []
			for (let i = 4; i >= 0; i--) {
				const value = maxHours - (range / 4) * i
				labels.push(Math.round(value))
			}
			return labels
		}
	},
	onLoad() {
		// 游客模式：允许访问，显示示例数据或空数据
		this.loadAllData()
	},
	onShow() {
		// 游客模式：允许访问
		// 页面显示时重新加载用户信息（从设置页面返回时）
		this.loadUserInfo()
	},
	methods: {
		async loadAllData() {
			this.loading = true
			try {
				// 并行加载所有数据，单个请求失败不影响其他请求
				const [user, stats, growthRecords, skills, weeklyData] = await Promise.all([
					profileAPI.getProfile().catch(() => null),
					profileAPI.getStats().catch(() => null),
					profileAPI.getGrowthRecords().catch(() => []),
					profileAPI.getSkills().catch(() => []),
					profileAPI.getWeeklyTraining().catch(() => [])
				])
				
				// 更新用户信息
				if (user) {
					this.userInfo.name = user.nickname || user.username || ''
					let descParts = []
					if (user.location) {
						descParts.push(user.location)
					}
					if (user.bio) {
						descParts.push(user.bio)
					}
					if (descParts.length > 0) {
						this.userInfo.desc = descParts.join(' · ')
					} else {
						this.userInfo.desc = user.phone || ''
					}
					this.avatarUrl = profileAPI.getAvatarUrl(user.avatar)
				}
				
				// 更新统计数据
				if (stats) {
					this.userInfo.stats = {
						matches: stats.matches || 0,
						goals: stats.goals || 0,
						assists: stats.assists || 0
					}
				}
				
				// 更新成长记录
				this.growthRecords = growthRecords || []
				
				// 更新技能评分
				this.skills = skills || []
				
				// 更新训练数据
				this.weeklyData = weeklyData || []
				
				// 计算本周变化
				if (this.weeklyData && this.weeklyData.length >= 2) {
					const thisWeek = this.weeklyData[this.weeklyData.length - 1]?.hours || 0
					const lastWeek = this.weeklyData[this.weeklyData.length - 2]?.hours || 0
					this.weeklyChange = thisWeek - lastWeek
				} else {
					this.weeklyChange = 0
				}
			} catch (error) {
				console.error('加载数据失败:', error)
				if (error.statusCode === 401) {
					authAPI.logout()
				} else {
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				}
			} finally {
				this.loading = false
			}
		},
		
		async loadUserInfo() {
			// 保留此方法用于从设置页面返回时刷新
			try {
				const user = await profileAPI.getProfile()
				if (user) {
					this.userInfo.name = user.nickname || user.username || ''
					let descParts = []
					if (user.location) {
						descParts.push(user.location)
					}
					if (user.bio) {
						descParts.push(user.bio)
					}
					if (descParts.length > 0) {
						this.userInfo.desc = descParts.join(' · ')
					} else {
						this.userInfo.desc = user.phone || ''
					}
					this.avatarUrl = profileAPI.getAvatarUrl(user.avatar)
				}
			} catch (error) {
				console.error('获取用户信息失败:', error)
				if (error.statusCode === 401) {
					authAPI.logout()
				}
			}
		},
		
		handleLogout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						authAPI.logout()
					}
				}
			})
		},
		
		goToSettings() {
			uni.navigateTo({
				url: '/pages/profile/settings'
			})
		},
		showGrowthDetail() {
			uni.showToast({
				title: '查看成长记录',
				icon: 'none'
			})
		},
		exportProfile() {
			uni.showToast({
				title: '导出中...',
				icon: 'loading',
				duration: 2000
			})
		},
		shareProfile() {
			// #ifdef MP-WEIXIN
			// 微信小程序分享
			uni.showShareMenu({
				withShareTicket: true,
				menus: ['shareAppMessage', 'shareTimeline']
			})
			// #endif
			
			// #ifdef APP-PLUS
			// App端分享
			plus.share.sendWithSystem({
				type: 'text',
				content: `我的足球档案 - ${this.userInfo.name}\n比赛场次：${this.userInfo.stats.matches}\n进球数：${this.userInfo.stats.goals}\n助攻数：${this.userInfo.stats.assists}`
			}, function() {
				uni.showToast({
					title: '分享成功',
					icon: 'success'
				})
			}, function(e) {
				uni.showToast({
					title: '分享失败',
					icon: 'none'
				})
			})
			// #endif
			
			// #ifdef H5
			// H5端分享
			if (navigator.share) {
				navigator.share({
					title: '我的足球档案',
					text: `我的足球档案 - ${this.userInfo.name}`,
					url: window.location.href
				}).then(() => {
					uni.showToast({
						title: '分享成功',
						icon: 'success'
					})
				}).catch(() => {
					uni.showToast({
						title: '分享取消',
						icon: 'none'
					})
				})
			} else {
				// 复制链接到剪贴板
				uni.setClipboardData({
					data: `我的足球档案 - ${this.userInfo.name}\n比赛场次：${this.userInfo.stats.matches}\n进球数：${this.userInfo.stats.goals}\n助攻数：${this.userInfo.stats.assists}`,
					success: () => {
						uni.showToast({
							title: '已复制到剪贴板',
							icon: 'success'
						})
					}
				})
			}
			// #endif
		}
	}
}
</script>

<style scoped>
.profile-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.profile-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 60rpx 30rpx 40rpx;
	margin-bottom: 30rpx;
	text-align: center;
	box-shadow: 0 4rpx 20rpx rgba(102, 126, 234, 0.3);
}

.avatar-section {
	position: relative;
	display: inline-block;
	margin-bottom: 20rpx;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	border: 4rpx solid #FFFFFF;
}

.edit-icon {
	position: absolute;
	bottom: 0;
	right: 0;
	width: 40rpx;
	height: 40rpx;
	background: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
}

.user-name {
	display: block;
	font-size: 36rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.user-desc {
	display: block;
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
	margin-bottom: 30rpx;
}

.user-stats {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
}

.stat-item {
	text-align: center;
}

.stat-value {
	display: block;
	font-size: 36rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 5rpx;
}

.stat-label {
	display: block;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.section {
	margin: 30rpx 20rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
}

.section-more {
	font-size: 26rpx;
	color: #999999;
}

.timeline {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.06);
}

.timeline-item {
	display: flex;
	padding: 20rpx 0;
	border-left: 2rpx solid #E0E0E0;
	padding-left: 30rpx;
	position: relative;
}

.timeline-item:last-child {
	border-left: none;
}

.timeline-dot {
	position: absolute;
	left: -8rpx;
	top: 30rpx;
	width: 16rpx;
	height: 16rpx;
	background: #3CB371;
	border-radius: 50%;
	border: 3rpx solid #FFFFFF;
	box-shadow: 0 0 0 2rpx #3CB371;
}

.timeline-content {
	flex: 1;
}

.timeline-date {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 5rpx;
}

.timeline-event {
	display: block;
	font-size: 28rpx;
	color: #333333;
}

.stats-container {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.chart-card {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.06);
	transition: transform 0.2s, box-shadow 0.2s;
}

.chart-card:active {
	transform: translateY(-2rpx);
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.chart-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 20rpx;
}

.chart-wrapper {
	position: relative;
}

.chart-container {
	display: flex;
	height: 300rpx;
	background: #FFFFFF;
	border-radius: 12rpx;
	overflow: hidden;
}

.chart-y-axis {
	width: 60rpx;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	padding: 40rpx 10rpx 50rpx 20rpx;
	background: #FAFAFA;
}

.y-label {
	font-size: 20rpx;
	color: #999999;
	text-align: right;
}

.chart-main {
	flex: 1;
	position: relative;
	padding: 40rpx 20rpx 50rpx 10rpx;
}

.chart-svg {
	width: 100%;
	height: 100%;
	display: block;
}

.chart-labels {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	pointer-events: none;
}

.chart-label-item {
	position: absolute;
	transform: translate(-50%, -100%);
	text-align: center;
	margin-top: -30rpx;
}

.label-value {
	display: block;
	font-size: 22rpx;
	color: #333333;
	font-weight: 600;
	white-space: nowrap;
	background: rgba(255, 255, 255, 0.9);
	padding: 4rpx 8rpx;
	border-radius: 6rpx;
}

.chart-x-labels {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 50rpx;
	display: flex;
	justify-content: space-around;
	align-items: center;
}

.x-label-item {
	position: absolute;
	transform: translateX(-50%);
	text-align: center;
}

.label-week {
	display: block;
	font-size: 20rpx;
	color: #999999;
	white-space: nowrap;
}

.chart-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #F0F0F0;
	gap: 20rpx;
}

.info-item {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.info-label {
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.info-value {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
}

.info-value.increase {
	color: #3CB371;
}

.info-value.decrease {
	color: #FF6B6B;
}

.skill-list {
	display: flex;
	flex-direction: column;
	gap: 25rpx;
}

.skill-item {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.skill-name {
	width: 100rpx;
	font-size: 26rpx;
	color: #333333;
}

.skill-bar {
	flex: 1;
	height: 14rpx;
	background: #F0F0F0;
	border-radius: 7rpx;
	overflow: hidden;
	box-shadow: inset 0 1rpx 3rpx rgba(0, 0, 0, 0.1);
}

.skill-fill {
	height: 100%;
	background: linear-gradient(90deg, #3CB371 0%, #4CD964 100%);
	border-radius: 7rpx;
	transition: width 0.5s ease-out;
	box-shadow: 0 2rpx 8rpx rgba(60, 179, 113, 0.3);
}

.skill-score {
	width: 80rpx;
	text-align: right;
	font-size: 26rpx;
	color: #3CB371;
	font-weight: 600;
}

.action-buttons {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.action-btn {
	padding: 24rpx;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
	transition: all 0.3s;
	cursor: pointer;
}

.action-btn.export {
	background: #FFFFFF;
	color: #333333;
	border: 2rpx solid #E0E0E0;
}

.action-btn.export:active {
	background: #F5F5F5;
	transform: scale(0.98);
}

.action-btn.share {
	background: #3CB371;
	color: #FFFFFF;
}

.action-btn.share:active {
	background: #2E8B57;
	transform: scale(0.98);
}

.logout-btn {
	width: 100%;
	padding: 24rpx;
	background: #FFFFFF;
	color: #FF6B6B;
	border: 2rpx solid #FFE0E0;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.logout-btn:active {
	background: #FFF5F5;
	transform: scale(0.98);
}
</style>

