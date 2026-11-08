<template>
	<view class="forgot-password-page">
		<view class="forgot-password-container">
			<!-- 标题 -->
			<view class="header-section">
				<text class="page-title">忘记密码</text>
				<text class="page-subtitle">请输入您的手机号，我们将发送验证码</text>
			</view>

			<!-- 步骤1: 输入手机号和验证码 -->
			<view class="form-section" v-if="step === 1">
				<view class="form-item">
					<text class="form-label">手机号</text>
					<input 
						class="form-input" 
						v-model="phone" 
						placeholder="请输入注册时使用的手机号"
						type="number"
						:disabled="loading"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">验证码</text>
					<view class="sms-input-wrapper">
						<input 
							class="form-input sms-input" 
							v-model="smsCode" 
							placeholder="请输入6位验证码"
							type="number"
							maxlength="6"
							:disabled="loading"
						/>
						<button 
							class="sms-btn" 
							:class="{ disabled: smsCountdown > 0 || !canSendSms || loading }"
							@click="sendSmsCode"
							:disabled="smsCountdown > 0 || !canSendSms || loading"
						>
							{{ smsCountdown > 0 ? `${smsCountdown}秒` : '获取验证码' }}
						</button>
					</view>
				</view>
				
				<button 
					class="submit-btn" 
					:class="{ loading: loading }"
					@click="handleRequestReset"
					:disabled="loading"
				>
					{{ loading ? '验证中...' : '下一步' }}
				</button>
				
				<view class="form-footer">
					<text class="link-text" @click="goToLogin">返回登录</text>
				</view>
			</view>

			<!-- 步骤2: 输入新密码 -->
			<view class="form-section" v-if="step === 2">
				<view class="success-tip">
					<text class="tip-icon">✓</text>
					<text class="tip-text">验证码验证成功，请设置新密码</text>
				</view>
				
				<view class="form-item">
					<text class="form-label">新密码</text>
					<input 
						class="form-input" 
						v-model="newPassword" 
						placeholder="请输入新密码（至少6个字符）"
						password
						:disabled="loading"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">确认新密码</text>
					<input 
						class="form-input" 
						v-model="confirmPassword" 
						placeholder="请再次输入新密码"
						password
						:disabled="loading"
					/>
				</view>
				
				<button 
					class="submit-btn" 
					:class="{ loading: loading }"
					@click="handleResetPassword"
					:disabled="loading"
				>
					{{ loading ? '重置中...' : '重置密码' }}
				</button>
				
				<view class="form-footer">
					<text class="link-text" @click="step = 1">返回上一步</text>
					<text class="link-text" @click="goToLogin">返回登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { authAPI } from '../../utils/api.js'

export default {
		data() {
		return {
			step: 1, // 1: 输入手机号和验证码, 2: 重置密码
			phone: '',
			smsCode: '',
			newPassword: '',
			confirmPassword: '',
			loading: false,
			smsCountdown: 0, // 验证码倒计时
			smsTimer: null // 倒计时定时器
		}
	},
	computed: {
		canSendSms() {
			// 手机号格式验证：11位数字，以1开头
			return this.phone && /^1[3-9]\d{9}$/.test(this.phone)
		}
	},
	beforeDestroy() {
		// 组件销毁时清除定时器
		if (this.smsTimer) {
			clearInterval(this.smsTimer)
			this.smsTimer = null
		}
	},
	methods: {
		async handleRequestReset() {
			// 验证手机号
			if (!this.phone.trim()) {
				uni.showToast({
					title: '请输入手机号',
					icon: 'none'
				})
				return
			}
			
			if (!/^1[3-9]\d{9}$/.test(this.phone.trim())) {
				uni.showToast({
					title: '请输入正确的手机号格式',
					icon: 'none'
				})
				return
			}
			
			// 验证验证码
			if (!this.smsCode.trim()) {
				uni.showToast({
					title: '请输入验证码',
					icon: 'none'
				})
				return
			}
			
			if (this.smsCode.trim().length !== 6) {
				uni.showToast({
					title: '验证码为6位数字',
					icon: 'none'
				})
				return
			}
			
			// 验证码会在重置密码时一起验证，这里先进入下一步
			this.step = 2
		},
		
		async handleResetPassword() {
			if (!this.newPassword.trim()) {
				uni.showToast({
					title: '请输入新密码',
					icon: 'none'
				})
				return
			}
			
			if (this.newPassword.length < 6) {
				uni.showToast({
					title: '密码至少6个字符',
					icon: 'none'
				})
				return
			}
			
			if (this.newPassword.length > 50) {
				uni.showToast({
					title: '密码最多50个字符',
					icon: 'none'
				})
				return
			}
			
			if (this.newPassword !== this.confirmPassword) {
				uni.showToast({
					title: '两次输入的密码不一致',
					icon: 'none'
				})
				return
			}
			
			this.loading = true
			
			try {
				await authAPI.resetPasswordBySms(this.phone.trim(), this.smsCode.trim(), this.newPassword)
				uni.showToast({
					title: '密码重置成功',
					icon: 'success'
				})
				
				// 跳转到登录页面
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/auth/login'
					})
				}, 1000)
			} catch (error) {
				console.error('重置密码失败:', error)
				let errorMsg = '重置密码失败，请重试'
				if (error.statusCode === 400 && error.data && error.data.detail) {
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
				this.loading = false
			}
		},
		
		async sendSmsCode() {
			// 验证手机号
			if (!this.canSendSms) {
				uni.showToast({
					title: '请输入正确的手机号',
					icon: 'none'
				})
				return
			}
			
			// 检查倒计时
			if (this.smsCountdown > 0) {
				return
			}
			
			this.loading = true
			
			try {
				await authAPI.sendSms(this.phone.trim(), 'reset_password')
				uni.showToast({
					title: '验证码已发送',
					icon: 'success'
				})
				
				// 开始倒计时
				this.smsCountdown = 60
				this.smsTimer = setInterval(() => {
					this.smsCountdown--
					if (this.smsCountdown <= 0) {
						clearInterval(this.smsTimer)
						this.smsTimer = null
					}
				}, 1000)
			} catch (error) {
				console.error('发送验证码失败:', error)
				let errorMsg = '发送验证码失败，请重试'
				if (error.statusCode === 400 && error.data && error.data.detail) {
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
				this.loading = false
			}
		},
		
		goToLogin() {
			uni.navigateTo({
				url: '/pages/auth/login'
			})
		}
	}
}
</script>

<style scoped>
.forgot-password-page {
	min-height: 100vh;
	background: #F5F5F5;
	padding: 40rpx;
	box-sizing: border-box;
	overflow-x: hidden;
}

.forgot-password-container {
	width: 100%;
	max-width: 700rpx;
	margin: 0 auto;
	box-sizing: border-box;
}

.header-section {
	text-align: center;
	margin-bottom: 60rpx;
	padding-top: 60rpx;
}

.page-title {
	display: block;
	font-size: 48rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 15rpx;
}

.page-subtitle {
	display: block;
	font-size: 28rpx;
	color: #999999;
}

.form-section {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 50rpx 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
	box-sizing: border-box;
}

.success-tip {
	display: flex;
	align-items: center;
	padding: 30rpx;
	background: #E8F5E9;
	border-radius: 12rpx;
	margin-bottom: 40rpx;
}

.tip-icon {
	font-size: 40rpx;
	color: #3CB371;
	margin-right: 20rpx;
}

.tip-text {
	flex: 1;
	font-size: 26rpx;
	color: #333333;
	line-height: 1.6;
}

.form-item {
	margin-bottom: 35rpx;
}

.form-label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 15rpx;
	font-weight: 500;
}

.form-input {
	width: 100%;
	height: 88rpx;
	padding: 0 30rpx;
	background: #F5F5F5;
	border-radius: 12rpx;
	font-size: 28rpx;
	color: #333333;
	box-sizing: border-box;
	line-height: 88rpx;
}

.sms-input-wrapper {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.sms-input {
	flex: 1;
}

.sms-btn {
	padding: 0 30rpx;
	height: 88rpx;
	background: #3CB371;
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 26rpx;
	white-space: nowrap;
	box-sizing: border-box;
	line-height: 88rpx;
}

.sms-btn.disabled {
	background: #CCCCCC;
	color: #999999;
	opacity: 0.6;
}

.submit-btn {
	width: 100%;
	padding: 28rpx;
	background: linear-gradient(135deg, #3CB371 0%, #2E8B57 100%);
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 600;
	margin-top: 30rpx;
	margin-bottom: 40rpx;
	box-sizing: border-box;
}

.submit-btn.loading {
	opacity: 0.7;
}

.submit-btn:disabled {
	opacity: 0.7;
}

.form-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.link-text {
	font-size: 26rpx;
	color: #3CB371;
}
</style>

