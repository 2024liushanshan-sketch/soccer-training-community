<template>
	<view class="home-page">
		<!-- 顶部Banner -->
		<view class="banner-container" v-if="bannerList.length > 0">
			<swiper class="banner-swiper" :autoplay="true" :interval="3000" :duration="500" circular>
				<swiper-item v-for="(item, index) in bannerList" :key="index" @click="handleBannerClick(item)">
					<view class="banner-item">
						<text class="banner-title">{{ item.title }}</text>
						<text class="banner-desc">{{ item.desc }}</text>
					</view>
				</swiper-item>
			</swiper>
		</view>

		<!-- 快捷入口宫格 -->
		<view class="grid-container">
			<view class="grid-item" v-for="item in gridItems" :key="item.id" @click="navigateTo(item.path)">
				<view class="grid-icon">{{ item.icon }}</view>
				<text class="grid-text">{{ item.text }}</text>
			</view>
		</view>

		<!-- 热门赛事 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">热门赛事</text>
				<text class="section-more" @click="navigateTo('/pages/match/index')">更多 ></text>
			</view>
			<scroll-view class="scroll-horizontal" scroll-x="true" show-scrollbar="false" v-if="hotMatches.length > 0">
				<view class="match-cards-wrapper">
					<view class="match-card" v-for="match in hotMatches" :key="match.id" @click="goToMatchDetail(match)">
						<text class="match-name">{{ match.name }}</text>
						<text class="match-date">{{ match.date }}</text>
					</view>
				</view>
			</scroll-view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无热门赛事</text>
			</view>
		</view>

		<!-- 推荐视频 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">推荐视频</text>
				<text class="section-more" @click="navigateTo('/pages/academy/index')">更多 ></text>
			</view>
			<view class="video-list" v-if="videos.length > 0">
				<view class="video-card" v-for="video in videos" :key="video.id" @click="navigateTo('/pages/academy/index')">
					<view class="video-cover">
						<image v-if="video.cover" class="cover-image" :src="video.cover" mode="aspectFill"></image>
						<text class="play-icon">▶</text>
					</view>
					<text class="video-title">{{ video.title }}</text>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无推荐视频</text>
			</view>
		</view>

		<!-- 足球知识卡片 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">足球知识</text>
			</view>
			<view class="knowledge-card">
				<text class="knowledge-title">{{ knowledge.title }}</text>
				<text class="knowledge-content">{{ knowledge.content }}</text>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../utils/api.js'

export default {
	data() {
		return {
			bannerList: [],
			gridItems: [
				{ id: 1, icon: '📋', text: '训练计划', path: '/pages/training/index' },
				{ id: 2, icon: '🏆', text: '赛事报名', path: '/pages/match/index' },
				{ id: 3, icon: '🎓', text: '技术学院', path: '/pages/academy/index' },
				{ id: 4, icon: '💪', text: '健康营养', path: '/pages/health/index' },
				{ id: 5, icon: '📊', text: '数据档案', path: '/pages/profile/index' },
				{ id: 6, icon: '💬', text: '社区', path: '/pages/community/index' }
			],
			hotMatches: [],
			videos: [],
			knowledge: {
				title: '',
				content: ''
			},
			loading: false
		}
	},
	onLoad() {
		this.loadData()
	},
	onPullDownRefresh() {
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
		})
	},
	methods: {
		async loadData() {
			this.loading = true
			try {
				// 并行加载所有数据，单个请求失败不影响其他请求
				const [banners, matches, videos, knowledge] = await Promise.all([
					request('/api/home/banners', 'GET').catch(() => []),
					request('/api/home/hot-matches', 'GET').catch(() => []),
					request('/api/home/recommended-videos', 'GET').catch(() => []),
					request('/api/home/knowledge', 'GET').catch(() => ({ title: '', content: '' }))
				])
				
				this.bannerList = banners || []
				this.hotMatches = (matches || []).map(match => ({
					id: match.id,
					name: match.name,
					date: this.formatDate(match.date)
				}))
				this.videos = videos || []
				this.knowledge = knowledge || { title: '', content: '' }
			} catch (error) {
				console.error('加载首页数据失败:', error)
				uni.showToast({
					title: '加载失败，请重试',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		formatDate(dateStr) {
			if (!dateStr) return ''
			try {
				const date = new Date(dateStr)
				if (isNaN(date.getTime())) return ''
				const month = date.getMonth() + 1
				const day = date.getDate()
				return `${month}月${day}日`
			} catch (e) {
				return ''
			}
		},
		goToMatchDetail(match) {
			// 跳转到比赛详情或比赛日体验页面
			if (match && match.id) {
				uni.navigateTo({
					url: `/pages/match-experience/index?match_id=${match.id}`
				})
			}
		},
		handleBannerClick(banner) {
			if (banner && banner.link_url) {
				this.navigateTo(banner.link_url)
			}
		},
		navigateTo(path) {
			// Tab Bar 页面列表
			const tabBarPages = [
				'/pages/home/index',
				'/pages/training/index',
				'/pages/match/index',
				'/pages/profile/index',
				'/pages/community/index'
			]
			
			// 判断是否为 Tab Bar 页面
			if (tabBarPages.includes(path)) {
				uni.switchTab({
					url: path
				})
			} else {
				uni.navigateTo({
					url: path
				})
			}
		}
	}
}
</script>

<style scoped>
.home-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.banner-container {
	margin: 30rpx 20rpx;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.banner-swiper {
	height: 200rpx;
}

.banner-item {
	height: 100%;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	padding: 40rpx;
}

.banner-title {
	font-size: 40rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.banner-desc {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.9);
}

.grid-container {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20rpx;
	margin: 30rpx 20rpx;
	padding: 30rpx;
	background: #FFFFFF;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.grid-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 20rpx;
	transition: transform 0.2s;
}

.grid-item:active {
	transform: scale(0.95);
}

.grid-icon {
	font-size: 60rpx;
	margin-bottom: 10rpx;
}

.grid-text {
	font-size: 26rpx;
	color: #333333;
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

.scroll-horizontal {
	width: 100%;
}

.match-cards-wrapper {
	display: flex;
	white-space: nowrap;
	align-items: stretch;
	padding-bottom: 10rpx;
}

.match-card {
	display: inline-flex;
	flex-direction: column;
	width: 200rpx;
	min-width: 200rpx;
	height: 140rpx;
	padding: 30rpx 20rpx;
	margin-right: 20rpx;
	background: #FFFFFF;
	border-radius: 16rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	vertical-align: top;
	flex-shrink: 0;
	box-sizing: border-box;
}

.match-name {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	line-height: 1.4;
	flex: 1;
}

.match-date {
	display: block;
	font-size: 24rpx;
	color: #999999;
	line-height: 1.4;
}

.video-list {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.video-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.video-cover {
	width: 100%;
	height: 200rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	position: relative;
}

.cover-image {
	width: 100%;
	height: 100%;
	position: absolute;
	top: 0;
	left: 0;
}

.video-cover:active .play-icon {
	transform: scale(1.2);
}

.play-icon {
	font-size: 60rpx;
	color: #FFFFFF;
	opacity: 0.9;
	transition: transform 0.2s;
}

.video-title {
	display: block;
	padding: 20rpx;
	font-size: 26rpx;
	color: #333333;
}

.knowledge-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.knowledge-title {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 15rpx;
}

.knowledge-content {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
}

.empty-state {
	padding: 60rpx 0;
	text-align: center;
	background: #FFFFFF;
	border-radius: 16rpx;
}

.empty-text {
	font-size: 26rpx;
	color: #999999;
}
</style>
