<template>
	<view class="academy-page">
		<!-- 搜索栏 -->
		<view class="search-bar">
			<input class="search-input" placeholder="搜索视频教程..." v-model="searchKeyword" />
			<text class="search-icon">🔍</text>
		</view>

		<!-- 分类标签 -->
		<scroll-view class="category-scroll" scroll-x>
			<view class="category-item" v-for="(cat, index) in categories" :key="index"
				:class="{ active: currentCategory === index }" @click="selectCategory(index)">
				<text>{{ cat }}</text>
			</view>
		</scroll-view>

		<!-- 视频教学区 -->
		<view class="video-section">
			<view class="video-card" v-for="video in filteredVideos" :key="video.id" @click="playVideo(video)">
				<view class="video-cover">
					<image class="cover-image" :src="video.cover" mode="aspectFill" />
					<view class="play-overlay">
						<text class="play-icon">▶</text>
					</view>
					<text class="video-duration">{{ video.duration }}</text>
				</view>
				<view class="video-info">
					<text class="video-title">{{ video.title }}</text>
					<text class="video-meta">{{ video.views }} 次观看 · {{ video.date }}</text>
				</view>
			</view>
		</view>

		<!-- 挑战模式入口 -->
		<view class="challenge-section">
			<view class="challenge-card" @click="showChallenge">
				<text class="challenge-icon">🎯</text>
				<view class="challenge-content">
					<text class="challenge-title">挑战模式</text>
					<text class="challenge-desc">每日训练任务，提升技能水平</text>
				</view>
				<text class="challenge-arrow">></text>
			</view>
		</view>

		<!-- 个性化训练计划 -->
		<view class="plan-section">
			<view class="section-header">
				<text class="section-title">个性化训练计划</text>
			</view>
			<view class="plan-card">
				<text class="plan-title">{{ personalPlan.title }}</text>
				<text class="plan-desc">{{ personalPlan.desc }}</text>
				<view class="plan-progress">
					<view class="progress-bar">
						<view class="progress-fill" :style="{ width: personalPlan.progress + '%' }"></view>
					</view>
					<text class="progress-text">{{ personalPlan.progress }}% 完成</text>
				</view>
			</view>
		</view>

		<!-- 挑战弹窗 -->
		<view class="modal" v-if="showChallengeModal" @click="closeChallenge">
			<view class="modal-content challenge-modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">今日挑战</text>
					<text class="modal-close" @click="closeChallenge">×</text>
				</view>
				<view class="challenge-list">
					<view class="challenge-item" v-for="task in dailyTasks" :key="task.id">
						<text class="task-icon">{{ task.completed ? '✓' : '○' }}</text>
						<text class="task-text" :class="{ completed: task.completed }">{{ task.text }}</text>
					</view>
				</view>
				<button class="start-btn" @click="startChallenge">开始挑战</button>
			</view>
		</view>

		<!-- 视频播放弹窗 -->
		<view class="modal" v-if="showVideoModal" @click="closeVideo">
			<view class="modal-content video-modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">{{ currentVideo.title }}</text>
					<text class="modal-close" @click="closeVideo">×</text>
				</view>
				<view class="video-player-container">
					<video 
						class="video-player"
						:src="currentVideo.url || ''"
						:poster="currentVideo.cover"
						controls
						:show-center-play-btn="true"
						:enable-play-gesture="true"
						:show-fullscreen-btn="true"
						:show-progress="true"
						:show-play-btn="true"
						object-fit="contain"
						@play="onVideoPlay"
						@pause="onVideoPause"
						@ended="onVideoEnded"
					></video>
				</view>
				<view class="video-detail">
					<text class="video-detail-title">{{ currentVideo.title }}</text>
					<text class="video-detail-meta">{{ currentVideo.views }} 次观看 · {{ currentVideo.date }}</text>
					<text class="video-detail-desc" v-if="currentVideo.desc">{{ currentVideo.desc }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { academyAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			searchKeyword: '',
			currentCategory: 0,
			categories: ['全部'],
			videos: [],
			personalPlan: {
				title: '本周训练计划',
				desc: '针对你的技术水平制定的个性化训练方案',
				progress: 0
			},
			showChallengeModal: false,
			showVideoModal: false,
			currentVideo: {},
			dailyTasks: [],
			loading: false
		}
	},
	onLoad() {
		this.loadData()
	},
	computed: {
		filteredVideos() {
			if (!Array.isArray(this.videos)) {
				return []
			}
			let result = this.videos
			// 分类筛选已在后端完成，这里只需要搜索筛选
			if (this.searchKeyword && typeof this.searchKeyword === 'string') {
				result = result.filter(v => v && v.title && typeof v.title === 'string' && v.title.includes(this.searchKeyword))
			}
			return result
		}
	},
	watch: {
		searchKeyword(newVal) {
			// 搜索关键词变化时重新加载
			if (newVal === '' || newVal.length >= 2) {
				this.loadVideos()
			}
		}
	},
	methods: {
		async loadData() {
			this.loading = true
			try {
				// 并行加载分类、视频和个性化计划
				const [categories, videos, plan] = await Promise.all([
					academyAPI.getCategories(),
					academyAPI.getVideos(),
					academyAPI.getPersonalPlan().catch(() => null)
				])
				
				// 处理分类列表（添加"全部"选项）
				this.categories = ['全部', ...(categories || []).map(c => c.name || c)]
				
				// 处理视频列表
				this.videos = (videos || []).map(video => ({
					id: video.id,
					title: video.title,
					cover: video.cover && typeof video.cover === 'string' 
						? (video.cover.startsWith('http') ? video.cover : (video.cover.startsWith('/') ? video.cover : '/uploads/' + video.cover))
						: '/static/video-default.jpg',
					duration: video.duration || '00:00',
					views: video.views || 0,
					date: video.date || '',
					category: video.category,
					url: video.url || '',
					desc: video.desc || ''
				}))
				
				// 处理个性化计划
				if (plan) {
					this.personalPlan = {
						title: plan.title || '本周训练计划',
						desc: plan.desc || '针对你的技术水平制定的个性化训练方案',
						progress: plan.progress || 0
					}
				}
			} catch (error) {
				console.error('加载数据失败:', error)
				uni.showToast({
					title: '加载失败，请重试',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		
		async loadVideos() {
			try {
				const categoryId = this.currentCategory > 0 ? this.currentCategory - 1 : null  // 减去"全部"选项
				const videos = await academyAPI.getVideos(categoryId, this.searchKeyword)
				this.videos = (videos || []).map(video => ({
					id: video.id,
					title: video.title,
					cover: video.cover && typeof video.cover === 'string' 
						? (video.cover.startsWith('http') ? video.cover : (video.cover.startsWith('/') ? video.cover : '/uploads/' + video.cover))
						: '/static/video-default.jpg',
					duration: video.duration || '00:00',
					views: video.views || 0,
					date: video.date || '',
					category: video.category,
					url: video.url || '',
					desc: video.desc || ''
				}))
			} catch (error) {
				console.error('加载视频失败:', error)
			}
		},
		async selectCategory(index) {
			if (typeof index !== 'number' || index < 0) {
				return
			}
			this.currentCategory = index
			await this.loadVideos()
		},
		async playVideo(video) {
			// 获取视频详情（更新观看次数）
			try {
				const videoDetail = await academyAPI.getVideo(video.id)
				this.currentVideo = {
					...video,
					...videoDetail
				}
			} catch (error) {
				console.error('获取视频详情失败:', error)
				this.currentVideo = video
			}
			this.showVideoModal = true
		},
		closeVideo() {
			this.showVideoModal = false
			this.currentVideo = {}
		},
		onVideoPlay() {
			// 视频开始播放
		},
		onVideoPause() {
			// 视频暂停
		},
		onVideoEnded() {
			// 视频播放结束
			uni.showToast({
				title: '播放完成',
				icon: 'success'
			})
		},
		async showChallenge() {
			this.showChallengeModal = true
			try {
				const tasks = await academyAPI.getDailyChallenges()
				this.dailyTasks = tasks || []
			} catch (error) {
				console.error('加载挑战任务失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
					this.closeChallenge()
				} else {
					this.dailyTasks = []
				}
			}
		},
		closeChallenge() {
			this.showChallengeModal = false
		},
		async startChallenge() {
			// 可以在这里实现开始挑战的逻辑
			uni.showToast({
				title: '挑战开始！',
				icon: 'success'
			})
			this.closeChallenge()
		}
	}
}
</script>

<style scoped>
.academy-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.search-bar {
	position: relative;
	margin: 20rpx;
	background: #FFFFFF;
	border-radius: 50rpx;
	padding: 20rpx 60rpx 20rpx 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.search-input {
	font-size: 28rpx;
	color: #333333;
}

.search-icon {
	position: absolute;
	right: 30rpx;
	top: 50%;
	transform: translateY(-50%);
	font-size: 32rpx;
}

.category-scroll {
	white-space: nowrap;
	padding: 0 20rpx;
	margin-bottom: 30rpx;
}

.category-item {
	display: inline-block;
	padding: 15rpx 30rpx;
	margin-right: 20rpx;
	background: #FFFFFF;
	border-radius: 30rpx;
	font-size: 26rpx;
	color: #666666;
}

.category-item.active {
	background: #3CB371;
	color: #FFFFFF;
}

.video-section {
	padding: 0 20rpx;
}

.video-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	margin-bottom: 30rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	transition: transform 0.2s;
}

.video-card:active {
	transform: scale(0.98);
}

.video-cover {
	position: relative;
	width: 100%;
	height: 400rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.cover-image {
	width: 100%;
	height: 100%;
}

.play-overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(0, 0, 0, 0.3);
	opacity: 0;
	transition: opacity 0.3s;
}

.video-card:active .play-overlay {
	opacity: 1;
}

.play-icon {
	font-size: 80rpx;
	color: #FFFFFF;
}

.video-duration {
	position: absolute;
	bottom: 10rpx;
	right: 10rpx;
	background: rgba(0, 0, 0, 0.7);
	color: #FFFFFF;
	padding: 5rpx 15rpx;
	border-radius: 8rpx;
	font-size: 22rpx;
}

.video-info {
	padding: 20rpx;
}

.video-title {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
}

.video-meta {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.challenge-section {
	padding: 0 20rpx;
	margin-bottom: 30rpx;
}

.challenge-card {
	background: linear-gradient(135deg, #3CB371 0%, #2E8B57 100%);
	border-radius: 16rpx;
	padding: 40rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(60, 179, 113, 0.3);
}

.challenge-icon {
	font-size: 60rpx;
	margin-right: 30rpx;
}

.challenge-content {
	flex: 1;
}

.challenge-title {
	display: block;
	font-size: 32rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.challenge-desc {
	display: block;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
}

.challenge-arrow {
	font-size: 40rpx;
	color: #FFFFFF;
}

.plan-section {
	padding: 0 20rpx;
}

.section-header {
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
}

.plan-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.plan-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.plan-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 20rpx;
}

.plan-progress {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.progress-bar {
	flex: 1;
	height: 8rpx;
	background: #E0E0E0;
	border-radius: 4rpx;
	overflow: hidden;
}

.progress-fill {
	height: 100%;
	background: #3CB371;
	border-radius: 4rpx;
	transition: width 0.3s;
}

.progress-text {
	font-size: 24rpx;
	color: #3CB371;
}

.modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.challenge-modal {
	width: 80%;
	max-width: 600rpx;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.modal-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
}

.modal-close {
	font-size: 48rpx;
	color: #999999;
	line-height: 1;
}

.challenge-list {
	margin-bottom: 30rpx;
}

.challenge-item {
	display: flex;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #F0F0F0;
}

.task-icon {
	font-size: 32rpx;
	color: #3CB371;
	margin-right: 20rpx;
}

.task-text {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
}

.task-text.completed {
	color: #999999;
	text-decoration: line-through;
}

.start-btn {
	width: 100%;
	padding: 24rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.video-modal {
	width: 90%;
	max-width: 700rpx;
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	max-height: 90vh;
	overflow-y: auto;
}

.video-player-container {
	width: 100%;
	margin-bottom: 20rpx;
	border-radius: 12rpx;
	overflow: hidden;
	background: #000000;
}

.video-player {
	width: 100%;
	height: 400rpx;
}

.video-detail {
	padding: 0 10rpx;
}

.video-detail-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.video-detail-meta {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 15rpx;
}

.video-detail-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
}
</style>

