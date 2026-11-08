<template>
	<view class="match-page">
		<!-- 本地赛事信息 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">本地赛事</text>
			</view>
			<view class="match-list">
				<view class="match-item" v-for="match in localMatches" :key="match.id">
					<view class="match-info" @click="showMatchDetail(match)">
						<text class="match-name">{{ match.name }}</text>
						<text class="match-date">{{ match.date }} {{ match.time }}</text>
						<text class="match-location">{{ match.location }}</text>
					</view>
					<view class="match-actions">
						<view class="match-status" :class="match.status">
							<text>{{ getStatusText(match.status) }}</text>
						</view>
						<button v-if="match.status === 'upcoming'" class="reg-btn-small" @click.stop="handleMatchRegistration(match)">
							报名
						</button>
					</view>
				</view>
			</view>
		</view>

		<!-- 在线报名 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">在线报名</text>
			</view>
			<view class="registration-card">
				<text class="reg-title">{{ registration.title }}</text>
				<text class="reg-desc">{{ registration.desc }}</text>
				<view class="reg-status">
					<text class="status-label">报名状态：</text>
					<text class="status-value" :class="registration.status">
						{{ registration.status === 'open' ? '报名中' : '已截止' }}
					</text>
				</view>
				<button class="reg-btn" :class="{ disabled: registration.status !== 'open' }" 
					@click="showRegistrationForm">
					{{ registration.status === 'open' ? '立即报名' : '报名已截止' }}
				</button>
			</view>
		</view>

		<!-- 赛程与战报 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">赛程与战报</text>
			</view>
			<view class="schedule-list">
				<view class="schedule-item" v-for="schedule in schedules" :key="schedule.id">
					<view class="schedule-date">
						<text class="date-day">{{ schedule.day }}</text>
						<text class="date-month">{{ schedule.month }}</text>
					</view>
					<view class="schedule-content">
						<text class="schedule-teams">{{ schedule.teamA }} vs {{ schedule.teamB }}</text>
						<text class="schedule-score" v-if="schedule.score">
							{{ schedule.score }}
						</text>
						<text class="schedule-time" v-else>{{ schedule.time }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 比赛直播 / MVP投票入口 -->
		<view class="section">
			<view class="action-cards">
				<view class="action-card" @click="goToLiveMatch">
					<text class="action-icon">📺</text>
					<text class="action-text">比赛直播</text>
				</view>
				<view class="action-card" @click="showMVPVote">
					<text class="action-icon">⭐</text>
					<text class="action-text">MVP投票</text>
				</view>
			</view>
		</view>

		<!-- 报名表单弹窗 -->
		<view class="modal" v-if="showForm" @click="closeForm">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">赛事报名</text>
					<text class="modal-close" @click="closeForm">×</text>
				</view>
				<view class="form-item">
					<text class="form-label">姓名</text>
					<input class="form-input" v-model="formData.name" placeholder="请输入姓名" :disabled="submitting" />
				</view>
				<view class="form-item">
					<text class="form-label">联系方式</text>
					<input class="form-input" v-model="formData.phone" placeholder="请输入手机号" type="number" :disabled="submitting" />
				</view>
				<view class="form-item">
					<text class="form-label">参赛项目</text>
					<input class="form-input" v-model="formData.event" placeholder="请选择参赛项目" :disabled="submitting" />
				</view>
				<button class="submit-btn" :class="{ loading: submitting }" @click="submitForm" :disabled="submitting">
					{{ submitting ? '提交中...' : '提交报名' }}
				</button>
			</view>
		</view>
	</view>
</template>

<script>
import { matchAPI } from '../../utils/api.js'

export default {
		data() {
		return {
			localMatches: [],
			registration: {
				title: '',
				desc: '',
				status: 'closed',
				match_id: null
			},
			currentMatchId: null, // 当前选中的赛事ID（用于报名）
			schedules: [],
			showForm: false,
			formData: {
				name: '',
				phone: '',
				event: ''
			},
			loading: false,
			submitting: false // 表单提交状态
		}
	},
	onLoad() {
		this.loadData()
	},
	methods: {
		async loadData() {
			this.loading = true
			try {
				// 检查登录状态
				const token = uni.getStorageSync('token')
				// 并行加载所有数据，单个请求失败不影响其他请求
				const [matches, registration, schedules] = await Promise.all([
					matchAPI.getLocalMatches().catch(() => []),
					token ? matchAPI.getRegistrations().catch(() => ({ title: '', desc: '', status: 'closed', match_id: null })) : Promise.resolve({ title: '', desc: '', status: 'closed', match_id: null }),
					matchAPI.getSchedules().catch(() => [])
				])
				
				// 处理赛事列表
				this.localMatches = (matches || []).map(match => ({
					id: match.id,
					name: match.name,
					date: this.formatDate(match.date),
					time: match.time || '',
					location: match.location || '',
					status: match.status
				}))
				
				// 处理报名信息
				this.registration = registration || { title: '', desc: '', status: 'closed', match_id: null }
				
				// 处理赛程列表
				this.schedules = (schedules || []).map(schedule => ({
					id: schedule.id,
					day: schedule.day,
					month: schedule.month,
					teamA: schedule.team_a,
					teamB: schedule.team_b,
					time: schedule.time,
					score: schedule.score
				}))
			} catch (error) {
				console.error('加载数据失败:', error)
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
		getStatusText(status) {
			const statusMap = {
				upcoming: '即将开始',
				ongoing: '进行中',
				finished: '已结束'
			}
			return statusMap[status] || '未知'
		},
		showMatchDetail(match) {
			// 跳转到比赛日体验页面，传递match_id
			uni.navigateTo({
				url: `/pages/match-experience/index?match_id=${match.id}`
			})
		},
		showRegistrationForm() {
			// 游客模式：允许访问，但操作时需要登录
			const token = uni.getStorageSync('token')
			if (!token) {
				uni.showToast({
					title: '请先登录后再报名',
					icon: 'none'
				})
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/auth/login'
					})
				}, 1500)
				return
			}
			
			if (this.registration.status === 'open') {
				this.showForm = true
			} else {
				uni.showToast({
					title: '报名已截止',
					icon: 'none'
				})
			}
		},
		handleMatchRegistration(match) {
			// 处理赛事列表中的报名按钮点击
			if (!match || !match.id) {
				return
			}
			
			// 游客模式：允许访问，但操作时需要登录
			const token = uni.getStorageSync('token')
			if (!token) {
				uni.showToast({
					title: '请先登录后再报名',
					icon: 'none'
				})
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/auth/login'
					})
				}, 1500)
				return
			}
			
			this.currentMatchId = match.id
			this.showForm = true
		},
		closeForm() {
			this.showForm = false
			// 清空表单和当前选中的赛事
			this.formData = {
				name: '',
				phone: '',
				event: ''
			}
			this.currentMatchId = null
		},
		async submitForm() {
			// 防止重复提交
			if (this.submitting) {
				return
			}
			
			// 表单验证
			if (!this.formData.name.trim()) {
				uni.showToast({
					title: '请输入姓名',
					icon: 'none'
				})
				return
			}
			
			if (!this.formData.phone.trim()) {
				uni.showToast({
					title: '请输入联系方式',
					icon: 'none'
				})
				return
			}
			
			// 验证手机号格式
			const phoneRegex = /^1[3-9]\d{9}$/
			if (!phoneRegex.test(this.formData.phone.trim())) {
				uni.showToast({
					title: '请输入正确的手机号格式',
					icon: 'none'
				})
				return
			}
			
			// 优先使用currentMatchId（从赛事列表点击的），否则使用registration.match_id（从在线报名区域点击的）
			const matchId = this.currentMatchId || this.registration.match_id
			
			if (!matchId) {
				uni.showToast({
					title: '请选择赛事',
					icon: 'none'
				})
				return
			}
			
			this.submitting = true
			try {
				await matchAPI.createRegistration({
					match_id: matchId,
					name: this.formData.name.trim(),
					phone: this.formData.phone.trim(),
					event: this.formData.event.trim() || null
				})
				
				uni.showToast({
					title: '报名成功',
					icon: 'success'
				})
				
				// 重新加载报名信息
				this.loadData()
				this.closeForm()
			} catch (error) {
				console.error('报名失败:', error)
				let errorMsg = '报名失败，请重试'
				
				if (error.statusCode === 401) {
					errorMsg = '请先登录'
					setTimeout(() => {
						uni.navigateTo({
							url: '/pages/auth/login'
						})
					}, 1500)
				} else if (error.statusCode === 400 && error.data && error.data.detail) {
					errorMsg = error.data.detail
				} else if (error.message) {
					errorMsg = error.message
				}
				
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 2000
				})
			} finally {
				this.submitting = false
			}
		},
		showMVPVote() {
			// 查找进行中的比赛，跳转到比赛日体验页面
			const liveMatch = this.localMatches.find(m => m.status === 'live' || m.status === 'ongoing')
			if (liveMatch) {
				uni.navigateTo({
					url: `/pages/match-experience/index?match_id=${liveMatch.id}`
				})
			} else {
				uni.showToast({
					title: '暂无进行中的比赛',
					icon: 'none'
				})
			}
		},
		goToLiveMatch() {
			// 查找进行中的比赛，跳转到比赛日体验页面
			const liveMatch = this.localMatches.find(m => m.status === 'live' || m.status === 'ongoing')
			if (liveMatch) {
				uni.navigateTo({
					url: `/pages/match-experience/index?match_id=${liveMatch.id}`
				})
			} else {
				uni.showToast({
					title: '暂无进行中的比赛',
					icon: 'none'
				})
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
.match-page {
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

.match-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.match-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.match-info {
	flex: 1;
}

.match-name {
	display: block;
	font-size: 30rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.match-date {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 5rpx;
}

.match-location {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.match-actions {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 10rpx;
}

.match-status {
	padding: 10rpx 20rpx;
	border-radius: 20rpx;
	font-size: 24rpx;
}

.match-status.upcoming {
	background: #E3F2FD;
	color: #1976D2;
}

.match-status.ongoing {
	background: #FFF3E0;
	color: #F57C00;
}

.match-status.finished {
	background: #F5F5F5;
	color: #999999;
}

.reg-btn-small {
	padding: 8rpx 20rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 20rpx;
	font-size: 24rpx;
	white-space: nowrap;
}

.registration-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.reg-title {
	display: block;
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 10rpx;
}

.reg-desc {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 20rpx;
}

.reg-status {
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
}

.status-label {
	font-size: 26rpx;
	color: #666666;
}

.status-value {
	font-size: 28rpx;
	font-weight: 600;
	margin-left: 10rpx;
}

.status-value.open {
	color: #3CB371;
}

.status-value.closed {
	color: #999999;
}

.reg-btn {
	width: 100%;
	padding: 24rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
}

.reg-btn.disabled {
	background: #E0E0E0;
	color: #999999;
}

.schedule-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.schedule-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.schedule-date {
	width: 100rpx;
	text-align: center;
	margin-right: 30rpx;
}

.date-day {
	display: block;
	font-size: 40rpx;
	font-weight: 600;
	color: #3CB371;
}

.date-month {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-top: 5rpx;
}

.schedule-content {
	flex: 1;
}

.schedule-teams {
	display: block;
	font-size: 30rpx;
	font-weight: 500;
	color: #333333;
	margin-bottom: 10rpx;
}

.schedule-score {
	display: block;
	font-size: 32rpx;
	font-weight: 600;
	color: #3CB371;
}

.schedule-time {
	display: block;
	font-size: 26rpx;
	color: #999999;
}

.action-cards {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
}

.action-card {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 40rpx;
	text-align: center;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.action-icon {
	display: block;
	font-size: 60rpx;
	margin-bottom: 15rpx;
}

.action-text {
	display: block;
	font-size: 28rpx;
	color: #333333;
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

.modal-content {
	width: 80%;
	max-width: 600rpx;
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 40rpx;
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

.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 10rpx;
}

.form-input {
	width: 100%;
	padding: 20rpx;
	background: #F5F5F5;
	border-radius: 12rpx;
	font-size: 28rpx;
	color: #333333;
}

.submit-btn {
	width: 100%;
	padding: 24rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 28rpx;
	margin-top: 20rpx;
}

.submit-btn:disabled,
.submit-btn.loading {
	background: #CCCCCC;
	color: #999999;
	opacity: 0.6;
}
</style>

