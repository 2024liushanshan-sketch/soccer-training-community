<template>
	<view class="match-experience-page">
		<!-- 实时比分与直播区域 -->
		<view class="live-section">
			<view class="match-header">
				<text class="match-title">{{ matchData.name || '比赛进行中' }}</text>
				<text class="match-status" :class="matchStatus">{{ getStatusText() }}</text>
			</view>
			<view class="score-board">
				<view class="team-info">
					<text class="team-name">{{ matchData.teamA }}</text>
					<text class="team-score">{{ matchData.scoreA }}</text>
				</view>
				<text class="score-divider">:</text>
				<view class="team-info">
					<text class="team-score">{{ matchData.scoreB }}</text>
					<text class="team-name">{{ matchData.teamB }}</text>
				</view>
			</view>
			<view class="match-time">
				<text>{{ matchData.time }}</text>
			</view>
		</view>

		<!-- 观众投票 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">MVP投票</text>
			</view>
			<view class="vote-list">
				<view class="vote-item" v-for="player in players" :key="player.id" @click="votePlayer(player.id)">
					<image class="player-avatar" :src="player.avatar" mode="aspectFill" />
					<view class="player-info">
						<text class="player-name">{{ player.name }}</text>
						<text class="player-position">{{ player.position }}</text>
					</view>
					<view class="vote-count">
						<text class="heart-icon" :class="{ voted: player.voted }">
							{{ player.voted ? '❤️' : '🤍' }}
						</text>
						<text class="vote-number">{{ player.votes }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 比赛录像与回放 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">比赛回放</text>
			</view>
			<view class="replay-list">
				<view class="replay-item" v-for="replay in replays" :key="replay.id" @click="playReplay(replay)">
					<view class="replay-cover">
						<text class="play-icon">▶</text>
						<text class="replay-duration">{{ replay.duration }}</text>
					</view>
					<view class="replay-info">
						<text class="replay-title">{{ replay.title }}</text>
						<text class="replay-time">{{ replay.time }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 线上助威墙 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">助威墙</text>
			</view>
			<view class="cheer-wall">
				<scroll-view class="cheer-scroll" scroll-y>
					<view class="cheer-item" v-for="(cheer, index) in cheers" :key="index">
						<text class="cheer-text">{{ cheer }}</text>
					</view>
				</scroll-view>
				<view class="cheer-input-area">
					<input class="cheer-input" v-model="newCheer" placeholder="输入助威语..." />
					<button class="cheer-btn" @click="sendCheer">发送</button>
				</view>
			</view>
		</view>

		<!-- 返回赛事中心 -->
		<view class="back-section">
			<button class="back-btn" @click="goToMatchCenter">返回赛事中心</button>
		</view>
	</view>
</template>

<script>
import { matchAPI } from '../../utils/api.js'
import { profileAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			matchId: null,
			matchStatus: 'live', // live, finished, upcoming
			matchData: {
				name: '',
				teamA: '',
				teamB: '',
				scoreA: 0,
				scoreB: 0,
				time: ''
			},
			players: [],
			replays: [],
			cheers: [],
			newCheer: '',
			updateTimer: null,
			loading: false
		}
	},
	onLoad(options) {
		// 从路由参数获取match_id
		if (options && options.match_id) {
			const matchId = parseInt(options.match_id)
			if (isNaN(matchId) || matchId <= 0) {
				uni.showToast({
					title: '比赛ID无效',
					icon: 'none'
				})
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/match/index'
					})
				}, 1500)
				return
			}
			this.matchId = matchId
		} else {
			// 如果没有match_id，跳转到赛事中心
			uni.showToast({
				title: '缺少比赛ID',
				icon: 'none'
			})
			setTimeout(() => {
				uni.switchTab({
					url: '/pages/match/index'
				})
			}, 1500)
			return
		}
		
		// 加载数据，数据加载完成后再检查是否需要启动自动更新
		this.loadData().then(() => {
			// 数据加载完成后，根据实际状态决定是否启动自动更新
			if (this.matchStatus === 'live' || this.matchStatus === 'ongoing') {
				this.startAutoUpdate()
			}
		}).catch(() => {
			// 加载失败时不做处理，错误已在 loadData 中处理
		})
	},
	onUnload() {
		if (this.updateTimer) {
			clearInterval(this.updateTimer)
		}
	},
	methods: {
		async loadData() {
			if (!this.matchId) return
			
			this.loading = true
			try {
				// 并行加载所有数据，单个请求失败不影响其他请求
				const [experience, players, replays, cheers] = await Promise.all([
					matchAPI.getMatchExperience(this.matchId).catch(() => null),
					matchAPI.getMatchPlayers(this.matchId).catch(() => []),
					matchAPI.getMatchReplays(this.matchId).catch(() => []),
					matchAPI.getMatchCheers(this.matchId).catch(() => [])
				])
				
				// 处理比赛数据
				if (experience && experience.match) {
					this.matchData = {
						name: experience.match.name,
						teamA: experience.match.team_a,
						teamB: experience.match.team_b,
						scoreA: experience.match.score_a || 0,
						scoreB: experience.match.score_b || 0,
						time: experience.match.time || ''
					}
					this.matchStatus = experience.match.status || 'live'
				}
				
				// 处理球员列表
				this.players = (players || []).map(player => ({
					id: player.id,
					name: player.name,
					position: player.position,
					avatar: profileAPI.getAvatarUrl(player.avatar),
					votes: player.votes || 0,
					voted: player.voted || false
				}))
				
				// 处理比赛回放
				this.replays = (replays || []).map(replay => ({
					id: replay.id,
					title: replay.title,
					duration: replay.duration || '00:00',
					time: replay.time || '',
					video_url: replay.video_url || ''
				}))
				
				// 处理助威墙
				this.cheers = (cheers || []).map(cheer => {
					if (typeof cheer === 'string') {
						return cheer
					}
					return cheer?.content || cheer?.text || ''
				}).filter(cheer => cheer) // 过滤空字符串
			} catch (error) {
				console.error('加载数据失败:', error)
				// 如果加载失败，停止自动更新
				if (this.updateTimer) {
					clearInterval(this.updateTimer)
					this.updateTimer = null
				}
				uni.showToast({
					title: '加载失败，请重试',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		getStatusText() {
			const statusMap = {
				live: '直播中',
				ongoing: '进行中',
				finished: '已结束',
				upcoming: '即将开始'
			}
			return statusMap[this.matchStatus] || '未知'
		},
		startAutoUpdate() {
			// 如果已有定时器，先清除
			if (this.updateTimer) {
				clearInterval(this.updateTimer)
				this.updateTimer = null
			}
			// 创建新的定时器
			this.updateTimer = setInterval(() => {
				// 实时更新数据（仅更新比分和球员得票数）
				if (this.matchId) {
					this.loadData()
				}
			}, 5000)
		},
		async votePlayer(playerId) {
			if (!this.matchId || !playerId) {
				uni.showToast({
					title: '参数无效',
					icon: 'none'
				})
				return
			}
			
			try {
				const result = await matchAPI.votePlayer(this.matchId, playerId)
				
				// 更新本地数据
				if (!Array.isArray(this.players)) {
					this.players = []
				}
				const player = this.players.find(p => p && p.id === playerId)
				if (player && result) {
					if (result.voted) {
						// 取消其他投票
						this.players.forEach(p => {
							if (p && p.id !== playerId && p.voted) {
								p.votes = Math.max(0, (p.votes || 0) - 1)
								p.voted = false
							}
						})
						player.voted = true
						player.votes = result.votes || 0
					} else {
						player.voted = false
						player.votes = result.votes || 0
					}
				}
			} catch (error) {
				console.error('投票失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
				} else {
					uni.showToast({
						title: error.message || '投票失败',
						icon: 'none'
					})
				}
			}
		},
		playReplay(replay) {
			if (!replay) {
				uni.showToast({
					title: '回放信息无效',
					icon: 'none'
				})
				return
			}
			
			if (replay.video_url) {
				// 可以在这里实现视频播放逻辑
				uni.showToast({
					title: '播放: ' + (replay.title || '回放视频'),
					icon: 'none'
				})
			} else {
				uni.showToast({
					title: '视频暂不可用',
					icon: 'none'
				})
			}
		},
		async sendCheer() {
			if (!this.newCheer || !this.newCheer.trim()) {
				return
			}
			
			if (!this.matchId) {
				uni.showToast({
					title: '比赛ID无效',
					icon: 'none'
				})
				return
			}
			
			try {
				await matchAPI.createCheer(this.matchId, this.newCheer.trim())
				// 确保 cheers 数组已初始化
				if (!Array.isArray(this.cheers)) {
					this.cheers = []
				}
				this.cheers.unshift(this.newCheer.trim())
				this.newCheer = ''
				uni.showToast({
					title: '助威成功！',
					icon: 'success'
				})
			} catch (error) {
				console.error('发送助威失败:', error)
				uni.showToast({
					title: error.message || '发送失败',
					icon: 'none'
				})
			}
		},
		goToMatchCenter() {
			uni.switchTab({
				url: '/pages/match/index'
			})
		}
	}
}
</script>

<style scoped>
.match-experience-page {
	background: #F5F5F5;
	padding-bottom: 120rpx;
}

.live-section {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 40rpx 30rpx;
	margin-bottom: 30rpx;
}

.match-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.match-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #FFFFFF;
}

.match-status {
	padding: 8rpx 20rpx;
	background: rgba(255, 255, 255, 0.3);
	border-radius: 20rpx;
	font-size: 24rpx;
	color: #FFFFFF;
}

.match-status.live {
	background: #FF4444;
}

.score-board {
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 20rpx;
}

.team-info {
	display: flex;
	flex-direction: column;
	align-items: center;
	flex: 1;
}

.team-name {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.9);
	margin-bottom: 15rpx;
}

.team-score {
	font-size: 80rpx;
	font-weight: 600;
	color: #FFFFFF;
}

.score-divider {
	font-size: 60rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin: 0 40rpx;
}

.match-time {
	text-align: center;
}

.match-time text {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
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

.vote-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.vote-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.player-avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	margin-right: 20rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.player-info {
	flex: 1;
}

.player-name {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 5rpx;
}

.player-position {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.vote-count {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.heart-icon {
	font-size: 40rpx;
	margin-bottom: 5rpx;
	transition: transform 0.2s;
}

.heart-icon.voted {
	animation: heartBeat 0.3s;
}

@keyframes heartBeat {
	0% { transform: scale(1); }
	50% { transform: scale(1.3); }
	100% { transform: scale(1); }
}

.vote-number {
	font-size: 24rpx;
	color: #666666;
}

.replay-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.replay-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.replay-cover {
	position: relative;
	width: 100%;
	height: 300rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	align-items: center;
	justify-content: center;
}

.play-icon {
	font-size: 80rpx;
	color: #FFFFFF;
	opacity: 0.9;
}

.replay-duration {
	position: absolute;
	bottom: 10rpx;
	right: 10rpx;
	background: rgba(0, 0, 0, 0.7);
	color: #FFFFFF;
	padding: 5rpx 15rpx;
	border-radius: 8rpx;
	font-size: 22rpx;
}

.replay-info {
	padding: 20rpx;
}

.replay-title {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
}

.replay-time {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.cheer-wall {
	background: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.cheer-scroll {
	max-height: 400rpx;
	padding: 20rpx;
}

.cheer-item {
	padding: 15rpx 20rpx;
	margin-bottom: 10rpx;
	background: #F5F5F5;
	border-radius: 12rpx;
	animation: slideIn 0.3s;
}

@keyframes slideIn {
	from {
		opacity: 0;
		transform: translateY(20rpx);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.cheer-text {
	font-size: 26rpx;
	color: #333333;
}

.cheer-input-area {
	display: flex;
	gap: 20rpx;
	padding: 20rpx;
	border-top: 1rpx solid #F0F0F0;
}

.cheer-input {
	flex: 1;
	padding: 20rpx;
	background: #F5F5F5;
	border-radius: 50rpx;
	font-size: 28rpx;
}

.cheer-btn {
	padding: 20rpx 40rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 50rpx;
	font-size: 28rpx;
}

.back-section {
	padding: 30rpx 20rpx;
}

.back-btn {
	width: 100%;
	padding: 24rpx;
	background: #FFFFFF;
	color: #333333;
	border: 2rpx solid #E0E0E0;
	border-radius: 12rpx;
	font-size: 28rpx;
}
</style>

