<template>
	<view class="splash-page">
		<view class="content">
			<image class="logo" src="/static/logo.png" mode="aspectFit"></image>
			<view class="text-area">
				<text class="title">Soccer App</text>
				<text class="subtitle">专业的足球训练平台</text>
			</view>
		</view>
		<view class="loading" v-if="loading">
			<text class="loading-text">加载中...</text>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				loading: true
			}
		},
		onLoad() {
			this.initApp()
		},
		methods: {
			initApp() {
				// 延迟1秒后跳转，模拟启动画面
				setTimeout(() => {
					this.checkLoginAndNavigate()
				}, 1000)
			},
			checkLoginAndNavigate() {
				// 游客模式：直接跳转到首页，不需要登录
				uni.switchTab({
					url: '/pages/home/index'
				})
			}
		}
	}
</script>

<style scoped>
	.splash-page {
		width: 100%;
		height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex: 1;
	}

	.logo {
		height: 200rpx;
		width: 200rpx;
		margin-bottom: 50rpx;
	}

	.text-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.title {
		font-size: 48rpx;
		font-weight: 600;
		color: #FFFFFF;
		margin-bottom: 20rpx;
	}

	.subtitle {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.9);
	}

	.loading {
		margin-bottom: 100rpx;
	}

	.loading-text {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.8);
	}
</style>
