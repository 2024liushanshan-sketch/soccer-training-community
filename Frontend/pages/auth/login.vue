<template>
	<view class="login-page">
		<view class="login-container">
			<!-- Logo区域 -->
			<view class="logo-section">
				<image class="logo" src="/static/logo.png" mode="aspectFit"></image>
				<text class="app-title">Soccer App</text>
				<text class="app-subtitle">足球应用</text>
			</view>

			<!-- 登录表单 -->
			<view class="form-section">
				<view class="form-item">
					<input 
						class="form-input" 
						v-model="formData.username" 
						placeholder="请输入用户名或手机号"
						:disabled="loading"
					/>
				</view>
				<view class="form-item">
					<input 
						class="form-input" 
						v-model="formData.password" 
						placeholder="请输入密码"
						password
						:disabled="loading"
					/>
				</view>
				
				<button 
					class="login-btn" 
					:class="{ loading: loading }"
					@click="handleLogin"
					:disabled="loading"
				>
					{{ loading ? '登录中...' : '登录' }}
				</button>
				
				<view class="form-footer">
					<text class="link-text" @click="goToRegister">还没有账号？立即注册</text>
					<text class="link-text" @click="goToForgotPassword">忘记密码？</text>
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
				password: ''
			},
			loading: false
		}
	},
	onLoad(options) {
		// 检查是否已登录
		const token = uni.getStorageSync('token')
		if (token) {
			uni.switchTab({
				url: '/pages/home/index'
			})
			return
		}
		// 优先使用URL参数中的用户名（从注册页面跳转过来）
		if (options && options.username) {
			this.formData.username = decodeURIComponent(options.username)
		} else {
			// 尝试加载保存的用户名
			const savedUsername = uni.getStorageSync('saved_username')
			if (savedUsername) {
				this.formData.username = savedUsername
			}
		}
	},
	methods: {
		async handleLogin() {
			// 表单验证
			if (!this.formData.username.trim()) {
				uni.showToast({
					title: '请输入用户名或手机号',
					icon: 'none'
				})
				return
			}
			
			if (!this.formData.password.trim()) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				})
				return
			}
			
			this.loading = true
			
			try {
				const res = await authAPI.login(this.formData.username.trim(), this.formData.password)
				// 保存用户名（可选）
				uni.setStorageSync('saved_username', this.formData.username.trim())
				
				uni.showToast({
					title: '登录成功',
					icon: 'success'
				})
				
				// 跳转到首页
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/home/index'
					})
				}, 1000)
			} catch (error) {
				console.error('登录失败:', error)
				let errorMsg = '登录失败，请重试'
				if (error.statusCode === 401) {
					errorMsg = '用户名或密码错误'
				} else if (error.data && error.data.detail) {
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
		
		goToRegister() {
			uni.navigateTo({
				url: '/pages/auth/register'
			})
		},
		
		goToForgotPassword() {
			uni.navigateTo({
				url: '/pages/auth/forgot-password'
			})
		}
	}
}
</script>

<style scoped>
.login-page {
	min-height: 100vh;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	padding: 40rpx;
	padding-top: 150rpx;
	box-sizing: border-box;
	overflow-x: hidden;
}

.login-container {
	width: 100%;
	max-width: 600rpx;
	margin: 0 auto;
	box-sizing: border-box;
}

.logo-section {
	text-align: center;
	margin-bottom: 80rpx;
}

.logo {
	width: 120rpx;
	height: 120rpx;
	margin-bottom: 30rpx;
}

.app-title {
	display: block;
	font-size: 48rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.app-subtitle {
	display: block;
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.form-section {
	background: #FFFFFF;
	border-radius: 30rpx;
	padding: 60rpx 40rpx;
	box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.2);
	box-sizing: border-box;
}

.form-item {
	margin-bottom: 30rpx;
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

.login-btn {
	width: 100%;
	padding: 28rpx;
	background: linear-gradient(135deg, #3CB371 0%, #2E8B57 100%);
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 600;
	margin-top: 20rpx;
	margin-bottom: 40rpx;
	box-sizing: border-box;
}

.login-btn.loading {
	opacity: 0.7;
}

.login-btn:disabled {
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

