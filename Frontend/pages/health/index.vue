<template>
	<view class="health-page">
		<!-- 营养指南 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">青少年运动营养指南</text>
			</view>
			<view class="guide-card" v-for="guide in nutritionGuides" :key="guide.id" @click="showDetail(guide)">
				<view class="guide-icon">{{ guide.icon }}</view>
				<view class="guide-content">
					<text class="guide-title">{{ guide.title }}</text>
					<text class="guide-desc">{{ guide.desc }}</text>
				</view>
				<text class="guide-arrow">></text>
			</view>
		</view>

		<!-- 休息与睡眠提醒 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">休息与睡眠监测</text>
			</view>
			<view class="sleep-card">
				<view class="sleep-stats">
					<view class="stat-item">
						<text class="stat-value">{{ sleepData.hours }}</text>
						<text class="stat-label">昨日睡眠</text>
					</view>
					<view class="stat-item">
						<text class="stat-value">{{ sleepData.quality }}</text>
						<text class="stat-label">睡眠质量</text>
					</view>
					<view class="stat-item">
						<text class="stat-value">{{ sleepData.goal }}h</text>
						<text class="stat-label">目标时长</text>
					</view>
				</view>
				<view class="sleep-tips">
					<text class="tip-title">💡 睡眠小贴士</text>
					<text class="tip-content">{{ sleepTips }}</text>
				</view>
			</view>
		</view>

		<!-- 运动损伤预防与康复 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">运动损伤预防与康复</text>
			</view>
			<view class="injury-card" v-for="item in injuryPrevention" :key="item.id" @click="showDetail(item)">
				<view class="injury-icon">{{ item.icon }}</view>
				<view class="injury-content">
					<text class="injury-title">{{ item.title }}</text>
					<text class="injury-desc">{{ item.desc }}</text>
				</view>
				<text class="collect-icon" :class="{ collected: item.collected }" @click.stop="toggleCollect(item.id)">
					{{ item.collected ? '❤️' : '🤍' }}
				</text>
			</view>
		</view>

		<!-- 健康监测 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">健康监测</text>
			</view>
			<view class="monitor-card">
				<text class="monitor-title">连接智能手环</text>
				<text class="monitor-desc">实时监测心率、步数等健康数据</text>
				<button class="connect-btn" @click="connectDevice">连接设备</button>
			</view>
			<view class="health-data" v-if="healthData">
				<view class="data-item">
					<text class="data-label">今日步数</text>
					<text class="data-value">{{ healthData.steps }}</text>
				</view>
				<view class="data-item">
					<text class="data-label">平均心率</text>
					<text class="data-value">{{ healthData.heartRate }} bpm</text>
				</view>
				<view class="data-item">
					<text class="data-label">消耗卡路里</text>
					<text class="data-value">{{ healthData.calories }} kcal</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { healthAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			nutritionGuides: [],
			sleepData: {
				hours: '0',
				quality: '无数据',
				goal: 9
			},
			sleepTips: '青少年建议每天睡眠8-10小时，保证充足休息有助于运动表现和身体恢复。',
			injuryPrevention: [],
			healthData: null,
			loading: false
		}
	},
	onLoad() {
		this.loadData()
	},
	methods: {
		async loadData() {
			this.loading = true
			try {
				// 并行加载所有数据，单个请求失败不影响其他请求
				const [guides, sleepData, tips, injuryPrevention, monitorData] = await Promise.all([
					healthAPI.getNutritionGuides().catch(() => []),
					healthAPI.getSleepData().catch(() => null),
					healthAPI.getSleepTips().catch(() => ({ tip: '青少年建议每天睡眠8-10小时，保证充足休息有助于运动表现和身体恢复。' })),
					healthAPI.getInjuryPrevention().catch(() => []),
					healthAPI.getMonitorData().catch(() => null)
				])
				
				// 处理营养指南
				this.nutritionGuides = (guides || []).map(guide => ({
					id: guide.id,
					icon: guide.icon || '🥗',
					title: guide.title,
					desc: guide.desc
				}))
				
				// 处理睡眠数据
				if (sleepData) {
					this.sleepData = {
						hours: sleepData.hours || '0',
						quality: sleepData.quality || '无数据',
						goal: sleepData.goal_hours || 9
					}
				}
				
				// 处理睡眠小贴士
				if (tips && tips.tip) {
					this.sleepTips = tips.tip
				}
				
				// 处理运动损伤预防
				this.injuryPrevention = (injuryPrevention || []).map(item => ({
					id: item.id,
					icon: item.icon || '🏥',
					title: item.title,
					desc: item.desc,
					collected: item.collected || false
				}))
				
				// 处理健康监测数据
				if (monitorData && monitorData.connected) {
					this.healthData = {
						steps: monitorData.steps || 0,
						heartRate: monitorData.heart_rate || 0,
						calories: monitorData.calories || 0
					}
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
		showDetail(item) {
			uni.showToast({
				title: item.title,
				icon: 'none'
			})
		},
		async toggleCollect(id) {
			if (!id) {
				uni.showToast({
					title: '内容ID无效',
					icon: 'none'
				})
				return
			}
			
			try {
				const result = await healthAPI.toggleCollect(id)
				if (!Array.isArray(this.injuryPrevention)) {
					this.injuryPrevention = []
				}
				const item = this.injuryPrevention.find(i => i && i.id === id)
				if (item && result) {
					item.collected = result.collected !== undefined ? result.collected : !item.collected
				}
			} catch (error) {
				console.error('收藏失败:', error)
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
		async connectDevice() {
			uni.showLoading({
				title: '正在连接设备...',
				mask: true
			})
			
			try {
				// 连接设备，从后端获取健康监测数据
				// 实际应用中，这里应该通过蓝牙或其他方式连接设备获取数据
				// 目前通过API创建/更新监测数据
				const result = await healthAPI.createMonitorData({
					steps: 0,
					heart_rate: null,
					calories: 0
				})
				
				if (result && result.connected) {
					this.healthData = {
						steps: result.steps || 0,
						heartRate: result.heart_rate || 0,
						calories: result.calories || 0
					}
					
					uni.showToast({
						title: '连接成功',
						icon: 'success'
					})
					
					// 重新加载监测数据
					this.loadData()
				}
			} catch (error) {
				console.error('连接设备失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
				} else {
					uni.showToast({
						title: error.message || '连接失败',
						icon: 'none'
					})
				}
			} finally {
				uni.hideLoading()
			}
		}
	}
}
</script>

<style scoped>
.health-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.section {
	margin: 30rpx 20rpx;
}

.section-header {
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
}

.guide-card,
.injury-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	transition: transform 0.2s;
}

.guide-card:active,
.injury-card:active {
	transform: scale(0.98);
}

.guide-icon,
.injury-icon {
	font-size: 50rpx;
	margin-right: 20rpx;
}

.guide-content,
.injury-content {
	flex: 1;
}

.guide-title,
.injury-title {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 8rpx;
}

.guide-desc,
.injury-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
}

.guide-arrow {
	font-size: 32rpx;
	color: #CCCCCC;
}

.collect-icon {
	font-size: 36rpx;
	margin-left: 10rpx;
}

.sleep-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.sleep-stats {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
	margin-bottom: 30rpx;
}

.stat-item {
	text-align: center;
}

.stat-value {
	display: block;
	font-size: 36rpx;
	font-weight: 600;
	color: #3CB371;
	margin-bottom: 10rpx;
}

.stat-label {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.sleep-tips {
	background: #F0F9F4;
	border-radius: 12rpx;
	padding: 20rpx;
}

.tip-title {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
}

.tip-content {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
}

.monitor-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.monitor-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.monitor-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 20rpx;
}

.connect-btn {
	width: 100%;
	padding: 24rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.health-data {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.data-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #F0F0F0;
}

.data-item:last-child {
	border-bottom: none;
}

.data-label {
	font-size: 28rpx;
	color: #666666;
}

.data-value {
	font-size: 32rpx;
	font-weight: 600;
	color: #3CB371;
}
</style>

