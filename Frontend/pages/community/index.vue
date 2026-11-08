<template>
	<view class="community-page">
		<!-- 话题区 -->
		<view class="section">
			<scroll-view class="topic-scroll" scroll-x>
				<view class="topic-tag" v-for="(topic, index) in topics" :key="index"
					:class="{ active: currentTopic === index }" @click="selectTopic(index)">
					<text># {{ typeof topic === 'string' ? topic : topic.name || topic }}</text>
				</view>
			</scroll-view>
		</view>

		<!-- 附近球友推荐 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">附近球友</text>
			</view>
			<scroll-view class="friends-scroll" scroll-x>
				<view class="friend-card" v-for="friend in nearbyFriends" :key="friend.id" @click="viewProfile(friend)">
					<image class="friend-avatar" :src="profileAPI.getAvatarUrl(friend.avatar)" mode="aspectFill" />
					<text class="friend-name">{{ friend.name }}</text>
					<text class="friend-distance">{{ friend.distance }}km</text>
				</view>
			</scroll-view>
		</view>

		<!-- 动态卡片流 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">最新动态</text>
			</view>
			<view class="post-list">
				<view class="post-card" v-for="post in posts" :key="post.id">
					<view class="post-header" @click="viewProfile(post.user)" v-if="post.user">
						<image class="post-avatar" :src="profileAPI.getAvatarUrl(post.user?.avatar)" mode="aspectFill" />
						<view class="post-user-info">
							<text class="post-username">{{ post.user?.name || '未知用户' }}</text>
							<text class="post-time">{{ post.time }}</text>
						</view>
					</view>
					<text class="post-content">{{ post.content }}</text>
					<view class="post-images" v-if="post.images && post.images.length > 0">
						<image class="post-image" v-for="(img, index) in post.images" :key="index" 
							:src="img && typeof img === 'string' ? (img.startsWith('http') ? img : (img.startsWith('/') ? img : '/uploads/' + img)) : '/static/image-default.jpg'" mode="aspectFill" />
					</view>
					<view class="post-topic" v-if="post.topic">
						<text># {{ post.topic }}</text>
					</view>
					<view class="post-actions">
						<view class="action-btn" @click="toggleLike(post.id)">
							<text class="action-icon" :class="{ liked: post.liked }">
								{{ post.liked ? '❤️' : '🤍' }}
							</text>
							<text class="action-count">{{ post.likes }}</text>
						</view>
						<view class="action-btn" @click="showComments(post.id)">
							<text class="action-icon">💬</text>
							<text class="action-count">{{ post.comments }}</text>
						</view>
						<view class="action-btn" @click="sharePost(post.id)">
							<text class="action-icon">📤</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 评论弹窗 -->
		<view class="modal" v-if="showCommentModal" @click="closeComments">
			<view class="modal-content comment-modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">评论</text>
					<text class="modal-close" @click="closeComments">×</text>
				</view>
				<scroll-view class="comment-list" scroll-y>
					<view class="comment-item" v-for="comment in comments" :key="comment.id">
						<image class="comment-avatar" :src="profileAPI.getAvatarUrl(comment.avatar)" mode="aspectFill" />
						<view class="comment-content">
							<text class="comment-name">{{ comment.name }}</text>
							<text class="comment-text">{{ comment.text }}</text>
						</view>
					</view>
				</scroll-view>
				<view class="comment-input-area">
					<input class="comment-input" v-model="newComment" placeholder="写评论..." />
					<button class="send-btn" @click="sendComment">发送</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { communityAPI } from '../../utils/api.js'
import { profileAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			currentTopic: 0,
			topics: [],
			nearbyFriends: [],
			posts: [],
			showCommentModal: false,
			currentPostId: null,
			comments: [],
			newComment: '',
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
				// 并行加载话题和动态，单个请求失败不影响其他请求
				const [topics, posts] = await Promise.all([
					communityAPI.getTopics().catch(() => []),
					communityAPI.getPosts().catch(() => [])
				])
				
				// 处理话题列表（添加"全部"选项）
				this.topics = ['全部', ...(topics || []).map(t => t.name)]
				
				// 处理动态列表
				this.posts = (posts || []).map(post => ({
					id: post.id,
					user: post.user,
					time: post.time,
					content: post.content,
					topic: post.topic,
					likes: post.likes,
					liked: post.liked,
					comments: post.comments,
					images: post.images || []
				}))
				
				// 加载附近球友（需要登录）
				try {
					const friends = await communityAPI.getNearbyFriends()
					this.nearbyFriends = friends || []
				} catch (error) {
					// 如果未登录，忽略错误
					console.log('获取附近球友失败（可能未登录）:', error)
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
		selectTopic(index) {
			if (typeof index !== 'number' || index < 0) {
				return
			}
			this.currentTopic = index
			// 重新加载动态（根据话题筛选）
			const topicId = index === 0 ? null : index - 1  // 减去"全部"选项
			this.loadPosts(topicId)
		},
		async loadPosts(topicId = null) {
			try {
				const posts = await communityAPI.getPosts(topicId)
				this.posts = (posts || []).map(post => ({
					id: post.id,
					user: post.user,
					time: post.time,
					content: post.content,
					topic: post.topic,
					likes: post.likes,
					liked: post.liked,
					comments: post.comments,
					images: post.images || []
				}))
			} catch (error) {
				console.error('加载动态失败:', error)
			}
		},
		viewProfile(user) {
			uni.navigateTo({
				url: '/pages/profile/index'
			})
		},
		async toggleLike(postId) {
			if (!postId) {
				uni.showToast({
					title: '动态ID无效',
					icon: 'none'
				})
				return
			}
			
			try {
				const result = await communityAPI.toggleLike(postId)
				if (!Array.isArray(this.posts)) {
					this.posts = []
				}
				const post = this.posts.find(p => p && p.id === postId)
				if (post && result) {
					post.liked = result.liked !== undefined ? result.liked : !post.liked
					post.likes = result.likes !== undefined ? result.likes : (post.likes || 0)
				}
			} catch (error) {
				console.error('点赞失败:', error)
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
		async showComments(postId) {
			if (!postId) {
				uni.showToast({
					title: '动态ID无效',
					icon: 'none'
				})
				return
			}
			
			this.currentPostId = postId
			this.showCommentModal = true
			try {
				const comments = await communityAPI.getComments(postId)
				this.comments = Array.isArray(comments) ? comments : []
			} catch (error) {
				console.error('加载评论失败:', error)
				this.comments = []
			}
		},
		closeComments() {
			this.showCommentModal = false
			this.newComment = ''
		},
		async sendComment() {
			if (!this.newComment || !this.newComment.trim()) {
				uni.showToast({
					title: '请输入评论内容',
					icon: 'none'
				})
				return
			}
			
			if (!this.currentPostId) {
				uni.showToast({
					title: '动态ID无效',
					icon: 'none'
				})
				return
			}
			
			try {
				const comment = await communityAPI.createComment(this.currentPostId, this.newComment.trim())
				if (!Array.isArray(this.comments)) {
					this.comments = []
				}
				if (comment) {
					this.comments.push(comment)
				}
				this.newComment = ''
				
				// 更新动态的评论数
				if (Array.isArray(this.posts)) {
					const post = this.posts.find(p => p && p.id === this.currentPostId)
					if (post) {
						post.comments = (post.comments || 0) + 1
					}
				}
			} catch (error) {
				console.error('发送评论失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
				} else {
					uni.showToast({
						title: error.message || '发送失败',
						icon: 'none'
					})
				}
			}
		},
		sharePost(postId) {
			const post = this.posts.find(p => p.id === postId)
			if (!post) return
			
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
				content: `${post.user?.name || '未知用户'}：${post.content}`
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
					title: (post.user?.name || '未知用户') + '的动态',
					text: post.content,
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
				// 复制内容到剪贴板
				uni.setClipboardData({
					data: `${post.user?.name || '未知用户'}：${post.content}`,
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
.community-page {
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

.topic-scroll {
	white-space: nowrap;
}

.topic-tag {
	display: inline-block;
	padding: 15rpx 30rpx;
	margin-right: 20rpx;
	background: #FFFFFF;
	border-radius: 30rpx;
	font-size: 26rpx;
	color: #666666;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.topic-tag.active {
	background: #3CB371;
	color: #FFFFFF;
}

.friends-scroll {
	white-space: nowrap;
}

.friend-card {
	display: inline-block;
	width: 150rpx;
	text-align: center;
	margin-right: 30rpx;
}

.friend-avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	margin-bottom: 10rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.friend-name {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 5rpx;
}

.friend-distance {
	display: block;
	font-size: 22rpx;
	color: #999999;
}

.post-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.post-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.post-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.post-avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin-right: 20rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.post-user-info {
	flex: 1;
}

.post-username {
	display: block;
	font-size: 28rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 5rpx;
}

.post-time {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.post-content {
	display: block;
	font-size: 28rpx;
	color: #333333;
	line-height: 1.6;
	margin-bottom: 20rpx;
}

.post-images {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 10rpx;
	margin-bottom: 20rpx;
}

.post-image {
	width: 100%;
	height: 200rpx;
	border-radius: 12rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.post-topic {
	margin-bottom: 20rpx;
}

.post-topic text {
	font-size: 24rpx;
	color: #3CB371;
}

.post-actions {
	display: flex;
	gap: 40rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #F0F0F0;
}

.action-btn {
	display: flex;
	align-items: center;
	gap: 10rpx;
	cursor: pointer;
	transition: all 0.2s;
	padding: 10rpx;
	border-radius: 8rpx;
}

.action-btn:active {
	background: #F5F5F5;
	transform: scale(0.95);
}

.action-icon {
	font-size: 32rpx;
	transition: transform 0.2s;
}

.action-icon.liked {
	animation: likeAnimation 0.3s;
}

@keyframes likeAnimation {
	0% { transform: scale(1); }
	50% { transform: scale(1.3); }
	100% { transform: scale(1); }
}

.action-count {
	font-size: 24rpx;
	color: #999999;
}

.modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: flex-end;
	z-index: 1000;
}

.comment-modal {
	width: 100%;
	max-height: 80vh;
	border-radius: 20rpx 20rpx 0 0;
	padding: 30rpx;
	display: flex;
	flex-direction: column;
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

.comment-list {
	flex: 1;
	margin-bottom: 20rpx;
}

.comment-item {
	display: flex;
	margin-bottom: 30rpx;
}

.comment-avatar {
	width: 60rpx;
	height: 60rpx;
	border-radius: 50%;
	margin-right: 20rpx;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.comment-content {
	flex: 1;
	background: #F5F5F5;
	border-radius: 12rpx;
	padding: 15rpx 20rpx;
}

.comment-name {
	display: block;
	font-size: 26rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 5rpx;
}

.comment-text {
	display: block;
	font-size: 26rpx;
	color: #666666;
}

.comment-input-area {
	display: flex;
	gap: 20rpx;
	align-items: center;
}

.comment-input {
	flex: 1;
	padding: 20rpx;
	background: #F5F5F5;
	border-radius: 50rpx;
	font-size: 28rpx;
}

.send-btn {
	padding: 20rpx 40rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 50rpx;
	font-size: 28rpx;
}
</style>

