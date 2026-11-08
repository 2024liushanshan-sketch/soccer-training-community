<template>
	<view class="settings-page">
		<view class="settings-container">
			<!-- 头像设置 -->
			<view class="section">
				<view class="section-title">头像</view>
				<view class="avatar-upload-section">
					<view class="avatar-preview" @click="chooseAvatar">
						<image 
							class="avatar-image" 
							:src="avatarPreview || '/static/avatar.png'" 
							mode="aspectFill"
						/>
						<view class="avatar-mask">
							<text class="avatar-text">点击更换</text>
						</view>
					</view>
					<text class="avatar-tip">支持 JPG、PNG 格式，大小不超过 5MB</text>
				</view>
			</view>

			<!-- 基本信息 -->
			<view class="section">
				<view class="section-title">基本信息</view>
				<view class="form-item">
					<text class="form-label">用户名</text>
					<input 
						class="form-input" 
						v-model="formData.username" 
						placeholder="请输入用户名（3-50个字符）"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">昵称</text>
					<input 
						class="form-input" 
						v-model="formData.nickname" 
						placeholder="请输入昵称（可选）"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">手机号</text>
					<input 
						class="form-input" 
						v-model="formData.phone" 
						placeholder="请输入手机号（可选）"
						type="number"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">位置</text>
					<input 
						class="form-input" 
						v-model="formData.location" 
						placeholder="请输入位置（可选）"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">个人简介</text>
					<textarea 
						class="form-textarea" 
						v-model="formData.bio" 
						placeholder="请输入个人简介（可选，最多500字）"
						maxlength="500"
					/>
					<text class="char-count">{{ formData.bio.length }}/500</text>
				</view>
			</view>

			<!-- 保存按钮 -->
			<view class="section">
				<button 
					class="save-btn" 
					:class="{ loading: saving }"
					@click="handleSave"
					:disabled="saving"
				>
					{{ saving ? '保存中...' : '保存' }}
				</button>
			</view>
		</view>
	</view>
</template>

<script>
import { profileAPI } from '../../utils/api.js'

export default {
	data() {
		return {
			formData: {
				username: '',
				nickname: '',
				phone: '',
				location: '',
				bio: ''
			},
			avatarPreview: '',
			avatarFile: null,
			saving: false
		}
	},
	onLoad() {
		this.loadProfile()
	},
	methods: {
		async loadProfile() {
			try {
				const user = await profileAPI.getProfile()
				if (user) {
					this.formData.username = user.username || ''
					this.formData.nickname = user.nickname || ''
					this.formData.phone = user.phone || ''
					this.formData.location = user.location || ''
					this.formData.bio = user.bio || ''
					this.avatarPreview = profileAPI.getAvatarUrl(user.avatar)
				}
			} catch (error) {
				console.error('加载资料失败:', error)
				uni.showToast({
					title: error.message || '加载失败',
					icon: 'none'
				})
			}
		},
		
		chooseAvatar() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					const tempFilePath = res.tempFilePaths[0]
					// 检查文件大小（5MB）
					uni.getFileInfo({
						filePath: tempFilePath,
						success: (fileInfo) => {
							if (fileInfo.size > 5 * 1024 * 1024) {
								uni.showToast({
									title: '图片大小不能超过5MB',
									icon: 'none'
								})
								return
							}
							this.avatarPreview = tempFilePath
							this.avatarFile = tempFilePath
						},
						fail: () => {
							uni.showToast({
								title: '获取文件信息失败',
								icon: 'none'
							})
						}
					})
				},
				fail: (err) => {
					console.error('选择图片失败:', err)
				}
			})
		},
		
		async handleSave() {
			// 表单验证
			if (!this.formData.username.trim()) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none'
				})
				return
			}
			
			if (this.formData.username.length < 3 || this.formData.username.length > 50) {
				uni.showToast({
					title: '用户名长度为3-50个字符',
					icon: 'none'
				})
				return
			}
			
			this.saving = true
			
			try {
				// 先上传头像（如果有）
				if (this.avatarFile) {
					uni.showLoading({
						title: '上传头像中...',
						mask: true
					})
					try {
						await profileAPI.uploadAvatar(this.avatarFile)
					} catch (uploadError) {
						uni.hideLoading()
						console.error('头像上传错误:', uploadError)
						uni.showToast({
							title: uploadError.message || '头像上传失败',
							icon: 'none',
							duration: 3000
						})
						return
					}
					uni.hideLoading()
				}
				
				// 更新其他资料
				const updateData = {}
				
				// 必填字段：必须发送（如果表单中有值）
				if (this.formData.username && this.formData.username.trim()) {
					updateData.username = this.formData.username.trim()
				}
				if (this.formData.phone && this.formData.phone.trim()) {
					updateData.phone = this.formData.phone.trim()
				}
				
				// 可选字段：始终发送（包括null值，用于清空字段）
				// 处理空字符串，转换为null
				updateData.phone = this.formData.phone && this.formData.phone.trim() ? this.formData.phone.trim() : null
				updateData.nickname = this.formData.nickname && this.formData.nickname.trim() ? this.formData.nickname.trim() : null
				updateData.location = this.formData.location && this.formData.location.trim() ? this.formData.location.trim() : null
				updateData.bio = this.formData.bio && this.formData.bio.trim() ? this.formData.bio.trim() : null
				
				// 只有当有数据要更新时才调用API
				// 如果只上传了头像，updateData可能为空，这是正常的
				if (Object.keys(updateData).length > 0) {
					await profileAPI.updateProfile(updateData)
				}
				
				uni.showToast({
					title: '保存成功',
					icon: 'success'
				})
				
				// 返回上一页
				setTimeout(() => {
					uni.navigateBack()
				}, 1000)
			} catch (error) {
				console.error('保存失败:', error)
				uni.showToast({
					title: error.message || '保存失败',
					icon: 'none',
					duration: 2000
				})
			} finally {
				this.saving = false
			}
		}
	}
}
</script>

<style scoped>
.settings-page {
	min-height: 100vh;
	background: #F5F5F5;
	padding-bottom: 40rpx;
}

.settings-container {
	padding: 30rpx 20rpx;
}

.section {
	background: #FFFFFF;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.06);
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333333;
	margin-bottom: 30rpx;
}

.avatar-upload-section {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.avatar-preview {
	position: relative;
	width: 200rpx;
	height: 200rpx;
	border-radius: 50%;
	overflow: hidden;
	margin-bottom: 20rpx;
	border: 4rpx solid #E0E0E0;
}

.avatar-image {
	width: 100%;
	height: 100%;
}

.avatar-mask {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s;
}

.avatar-preview:active .avatar-mask {
	opacity: 1;
}

.avatar-text {
	color: #FFFFFF;
	font-size: 24rpx;
}

.avatar-tip {
	font-size: 24rpx;
	color: #999999;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-item:last-child {
	margin-bottom: 0;
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

.form-textarea {
	width: 100%;
	min-height: 200rpx;
	padding: 20rpx 30rpx;
	background: #F5F5F5;
	border-radius: 12rpx;
	font-size: 28rpx;
	color: #333333;
	box-sizing: border-box;
}

.char-count {
	display: block;
	text-align: right;
	font-size: 24rpx;
	color: #999999;
	margin-top: 10rpx;
}

.save-btn {
	width: 100%;
	padding: 28rpx;
	background: linear-gradient(135deg, #3CB371 0%, #2E8B57 100%);
	color: #FFFFFF;
	border: none;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 600;
}

.save-btn.loading {
	opacity: 0.7;
}

.save-btn:disabled {
	opacity: 0.7;
}
</style>

