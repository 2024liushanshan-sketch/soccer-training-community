<template>
	<view class="register-page">
		<view class="register-container">
			<!-- 标题 -->
			<view class="header-section">
				<text class="page-title">注册账号</text>
				<text class="page-subtitle">创建您的Soccer App账号</text>
			</view>

			<!-- 注册表单 -->
			<view class="form-section">
				<view class="form-item">
					<text class="form-label">用户名</text>
					<input 
						class="form-input" 
						v-model="formData.username" 
						placeholder="请输入用户名（3-50个字符）"
						:disabled="loading"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">手机号</text>
					<input 
						class="form-input" 
						v-model="formData.phone" 
						placeholder="请输入手机号"
						type="number"
						:disabled="loading"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">验证码</text>
					<view class="sms-input-wrapper">
						<input 
							class="form-input sms-input" 
							v-model="formData.smsCode" 
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
				
				<view class="form-item">
					<text class="form-label">密码</text>
					<input 
						class="form-input" 
						v-model="formData.password" 
						placeholder="请输入密码（至少6个字符）"
						password
						:disabled="loading"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">确认密码</text>
					<input 
						class="form-input" 
						v-model="formData.confirmPassword" 
						placeholder="请再次输入密码"
						password
						:disabled="loading"
					/>
				</view>
				
				<button 
					class="register-btn" 
					:class="{ loading: loading }"
					@click="handleRegister"
					:disabled="loading"
				>
					{{ loading ? '注册中...' : '立即注册' }}
				</button>
				
				<view class="form-footer">
					<text class="link-text" @click="goToLogin">已有账号？立即登录</text>
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
			formData: {
				username: '',
				phone: '',
				password: '',
				confirmPassword: '',
				smsCode: ''
			},
			loading: false,
			smsCountdown: 0, // 验证码倒计时
			smsTimer: null // 倒计时定时器
		}
	},
	computed: {
		canSendSms() {
			// 手机号格式验证：11位数字，以1开头
			return this.formData.phone && /^1[3-9]\d{9}$/.test(this.formData.phone)
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
		validateForm() {
			if (!this.formData.username.trim()) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none'
				})
				return false
			}
			
			if (this.formData.username.length < 3 || this.formData.username.length > 50) {
				uni.showToast({
					title: '用户名长度为3-50个字符',
					icon: 'none'
				})
				return false
			}
			
			// 验证手机号
			if (!this.formData.phone.trim()) {
				uni.showToast({
					title: '请输入手机号',
					icon: 'none'
				})
				return false
			}
			
			if (!/^1[3-9]\d{9}$/.test(this.formData.phone.trim())) {
				uni.showToast({
					title: '请输入正确的手机号格式',
					icon: 'none'
				})
				return false
			}
			
			// 验证验证码
			if (!this.formData.smsCode.trim()) {
				uni.showToast({
					title: '请输入验证码',
					icon: 'none'
				})
				return false
			}
			
			if (this.formData.smsCode.trim().length !== 6) {
				uni.showToast({
					title: '验证码为6位数字',
					icon: 'none'
				})
				return false
			}
			
			if (!this.formData.password.trim()) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				})
				return false
			}
			
			if (this.formData.password.length < 6) {
				uni.showToast({
					title: '密码至少6个字符',
					icon: 'none'
				})
				return false
			}
			
			if (this.formData.password.length > 50) {
				uni.showToast({
					title: '密码最多50个字符',
					icon: 'none'
				})
				return false
			}
			
			if (this.formData.password !== this.formData.confirmPassword) {
				uni.showToast({
					title: '两次输入的密码不一致',
					icon: 'none'
				})
				return false
			}
			
			return true
		},
		
		async handleRegister() {
			if (!this.validateForm()) {
				return
			}
			
			this.loading = true
			
			try {
				const registerData = {
					username: this.formData.username.trim(),
					phone: this.formData.phone.trim(),
					password: this.formData.password,
					sms_code: this.formData.smsCode.trim()
				}
				
				await authAPI.registerWithSms(registerData)
				
				uni.showToast({
					title: '注册成功',
					icon: 'success'
				})
				
				// 跳转到登录页面，并传递用户名
				setTimeout(() => {
					uni.redirectTo({
						url: `/pages/auth/login?username=${encodeURIComponent(this.formData.username.trim())}`
					})
				}, 1000)
			} catch (error) {
				console.error('注册失败:', error)
				let errorMsg = '注册失败，请重试'
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
				await authAPI.sendSms(this.formData.phone.trim(), 'register')
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
		}
	}
}
</script>

<style scoped>
.register-page {
	min-height: 100vh;
	background: #F5F5F5;
	padding: 40rpx;
	box-sizing: border-box;
	overflow-x: hidden;
}

.register-container {
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

.register-btn {
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

.register-btn.loading {
	opacity: 0.7;
}

.register-btn:disabled {
	opacity: 0.7;
}

.form-footer {
	text-align: center;
}

.link-text {
	font-size: 26rpx;
	color: #3CB371;
}
</style>

