// API基础配置
let BASE_URL = 'http://127.0.0.1:8000'

// #ifdef H5
BASE_URL = 'http://127.0.0.1:8000'
// #endif

// 请求封装
export function request(url, method = 'GET', data = {}, header = {}) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + url,
			method: method,
			data: data,
			header: {
				'Content-Type': 'application/json',
				...header
			},
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					// 游客模式：401错误不强制跳转登录，允许继续使用
					if (res.statusCode === 401 && header['Authorization']) {
						// 清除token和用户信息，但不跳转（游客模式）
						uni.removeStorageSync('token')
						uni.removeStorageSync('user')
						console.log('游客模式：token已清除，继续使用')
					}
					// 处理错误响应
					reject({
						statusCode: res.statusCode,
						data: res.data,
						message: res.data?.detail || res.data?.message || '请求失败'
					})
				}
			},
			fail: (err) => {
				reject({
					statusCode: 0,
					message: err.errMsg || '网络请求失败，请检查网络连接'
				})
			}
		})
	})
}

// 带token的请求
export function requestWithToken(url, method = 'GET', data = {}) {
	const token = uni.getStorageSync('token')
	if (!token) {
		return Promise.reject({
			statusCode: 401,
			message: '未登录，请先登录'
		})
	}
	return request(url, method, data, {
		'Authorization': `Bearer ${token}`
	})
}

// 认证相关API
export const authAPI = {
	// 注册
	register(data) {
		return request('/api/auth/register', 'POST', data)
	},
	
	// 登录
	login(username, password) {
		// 使用form-data格式（OAuth2标准格式）
		const formData = `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
		
		return new Promise((resolve, reject) => {
			uni.request({
				url: BASE_URL + '/api/auth/login',
				method: 'POST',
				data: formData,
				header: {
					'Content-Type': 'application/x-www-form-urlencoded'
				},
				success: (res) => {
					if (res.statusCode >= 200 && res.statusCode < 300) {
						// 保存token和用户信息
						uni.setStorageSync('token', res.data.access_token)
						uni.setStorageSync('user', res.data.user)
						resolve(res.data)
					} else {
						// 统一错误处理格式
						reject({
							statusCode: res.statusCode,
							data: res.data,
							message: res.data?.detail || res.data?.message || '登录失败'
						})
					}
				},
				fail: (err) => {
					reject({
						statusCode: 0,
						message: err.errMsg || '网络请求失败，请检查网络连接'
					})
				}
			})
		})
	},
	
	// 获取当前用户信息
	getCurrentUser() {
		return requestWithToken('/api/auth/me', 'GET')
	},
	
	
	// 退出登录
	logout() {
		uni.removeStorageSync('token')
		uni.removeStorageSync('user')
		uni.reLaunch({
			url: '/pages/auth/login'
		})
	},
	
	// 发送短信验证码
	sendSms(phone, scene) {
		return request('/api/auth/send-sms', 'POST', {
			phone,
			scene
		})
	},
	
	// 带验证码注册
	registerWithSms(data) {
		return request('/api/auth/register-with-sms', 'POST', data)
	},
	
	// 验证码重置密码
	resetPasswordBySms(phone, smsCode, newPassword) {
		return request('/api/auth/reset-password-with-sms', 'POST', {
			phone,
			sms_code: smsCode,
			new_password: newPassword
		})
	}
}

// 个人资料相关API
export const profileAPI = {
	// 获取个人资料
	getProfile() {
		return requestWithToken('/api/profile/me', 'GET')
	},
	
	// 更新个人资料
	updateProfile(data) {
		return requestWithToken('/api/profile/me', 'PUT', data)
	},
	
	// 上传头像
	uploadAvatar(filePath) {
		return new Promise((resolve, reject) => {
			const token = uni.getStorageSync('token')
			if (!token) {
				reject({
					statusCode: 401,
					message: '未登录，请先登录'
				})
				return
			}
			
			uni.uploadFile({
				url: BASE_URL + '/api/profile/avatar',
				filePath: filePath,
				name: 'file',
				header: {
					'Authorization': `Bearer ${token}`
				},
				formData: {},
				success: (res) => {
					console.log('上传响应:', res)
					if (res.statusCode >= 200 && res.statusCode < 300) {
						try {
							const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
							resolve(data)
						} catch (e) {
							console.error('解析响应失败:', e, res.data)
							resolve(res.data)
						}
					} else {
						let errorData = {}
						try {
							errorData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
						} catch (e) {
							errorData = { detail: res.data || '上传失败' }
						}
						reject({
							statusCode: res.statusCode,
							data: errorData,
							message: errorData.detail || errorData.message || '上传失败'
						})
					}
				},
				fail: (err) => {
					console.error('上传失败:', err)
					reject({
						statusCode: 0,
						message: err.errMsg || '网络请求失败，请检查网络连接'
					})
				}
			})
		})
	},
	
	// 获取头像URL
	getAvatarUrl(avatarPath) {
		if (!avatarPath) {
			return '/static/avatar.png'
		}
		// 如果是相对路径，拼接BASE_URL
		if (avatarPath.startsWith('uploads/')) {
			return BASE_URL + '/' + avatarPath
		}
		// 如果已经是完整URL，直接返回
		if (avatarPath.startsWith('http')) {
			return avatarPath
		}
		return BASE_URL + '/' + avatarPath
	},
	
	// 获取用户统计数据
	getStats() {
		return requestWithToken('/api/profile/stats', 'GET')
	},
	
	// 获取成长记录
	getGrowthRecords(limit = 10) {
		return requestWithToken('/api/profile/growth-records', 'GET', { limit })
	},
	
	// 获取用户技能评分
	getSkills() {
		return requestWithToken('/api/profile/skills', 'GET')
	},
	
	// 获取过去N周的训练时长数据
	getWeeklyTraining(weeks = 7) {
		return requestWithToken('/api/profile/weekly-training', 'GET', { weeks })
	}
}

// 赛事中心相关API
export const matchAPI = {
	// 获取本地赛事列表
	getLocalMatches() {
		return request('/api/match/local', 'GET')
	},
	
	// 获取赛事详情
	getMatch(matchId) {
		return request(`/api/match/${matchId}`, 'GET')
	},
	
	// 获取在线报名信息
	getRegistrations() {
		return requestWithToken('/api/match/registrations', 'GET')
	},
	
	// 提交赛事报名
	createRegistration(data) {
		return requestWithToken('/api/match/registrations', 'POST', data)
	},
	
	// 获取赛程与战报列表
	getSchedules(limit = 10) {
		return request('/api/match/schedules', 'GET', { limit })
	},
	
	// 获取指定赛事的赛程
	getMatchSchedules(matchId) {
		return request(`/api/match/${matchId}/schedules`, 'GET')
	},
	
	// 获取比赛日体验数据
	getMatchExperience(matchId) {
		return request(`/api/match/${matchId}/experience`, 'GET')
	},
	
	// 获取比赛球员列表
	getMatchPlayers(matchId) {
		const user = uni.getStorageSync('user')
		const params = user && user.id ? { current_user_id: user.id } : {}
		return request(`/api/match/${matchId}/players`, 'GET', params)
	},
	
	// 为球员投票
	votePlayer(matchId, playerId) {
		return requestWithToken(`/api/match/${matchId}/vote`, 'POST', { player_id: playerId })
	},
	
	// 获取比赛回放列表
	getMatchReplays(matchId) {
		return request(`/api/match/${matchId}/replays`, 'GET')
	},
	
	// 获取助威墙列表
	getMatchCheers(matchId, limit = 50) {
		return request(`/api/match/${matchId}/cheers`, 'GET', { limit })
	},
	
	// 发送助威语
	createCheer(matchId, content) {
		return request(`/api/match/${matchId}/cheers`, 'POST', { content })
	}
}

// 训练中心相关API
export const trainingAPI = {
	// 获取训练计划列表
	getPlans(date) {
		const params = date ? { date } : {}
		return requestWithToken('/api/training/plans', 'GET', params)
	},
	
	// 创建训练计划
	createPlan(data) {
		return requestWithToken('/api/training/plans', 'POST', data)
	},
	
	// 更新训练计划
	updatePlan(planId, data) {
		return requestWithToken(`/api/training/plans/${planId}`, 'PUT', data)
	},
	
	// 删除训练计划
	deletePlan(planId) {
		return requestWithToken(`/api/training/plans/${planId}`, 'DELETE')
	},
	
	// 训练计划打卡
	checkPlan(planId) {
		return requestWithToken(`/api/training/plans/${planId}/check`, 'POST')
	},
	
	// 获取训练统计数据
	getStats() {
		return requestWithToken('/api/training/stats', 'GET')
	},
	
	// 获取数据分析数据
	getAnalysis() {
		return requestWithToken('/api/training/analysis', 'GET')
	},
	
	// 获取教练社区动态列表
	getCoachPosts() {
		return request('/api/training/coach-posts', 'GET')
	},
	
	// 发布教练社区动态
	createCoachPost(data) {
		return requestWithToken('/api/training/coach-posts', 'POST', data)
	}
}

// 社区相关API
export const communityAPI = {
	// 获取话题列表
	getTopics() {
		return request('/api/community/topics', 'GET')
	},
	
	// 获取附近球友
	getNearbyFriends(latitude, longitude) {
		const params = {}
		if (latitude !== undefined && longitude !== undefined) {
			params.latitude = latitude
			params.longitude = longitude
		}
		return requestWithToken('/api/community/nearby-friends', 'GET', params)
	},
	
	// 获取社区动态列表
	getPosts(topicId, limit = 20, offset = 0) {
		const params = { limit, offset }
		if (topicId) {
			params.topic_id = topicId
		}
		// 尝试获取当前用户ID（如果已登录）
		const user = uni.getStorageSync('user')
		if (user && user.id) {
			params.current_user_id = user.id
		}
		return request('/api/community/posts', 'GET', params)
	},
	
	// 发布动态
	createPost(data) {
		return requestWithToken('/api/community/posts', 'POST', data)
	},
	
	// 点赞/取消点赞
	toggleLike(postId) {
		return requestWithToken(`/api/community/posts/${postId}/like`, 'POST')
	},
	
	// 获取评论列表
	getComments(postId) {
		return request(`/api/community/posts/${postId}/comments`, 'GET')
	},
	
	// 发表评论
	createComment(postId, content) {
		return requestWithToken(`/api/community/posts/${postId}/comments`, 'POST', { content })
	}
}

// 技术学院相关API
export const academyAPI = {
	// 获取视频分类列表
	getCategories() {
		return request('/api/academy/categories', 'GET')
	},
	
	// 获取视频列表
	getVideos(categoryId, keyword, limit = 50, offset = 0) {
		const params = { limit, offset }
		if (categoryId) {
			params.category_id = categoryId
		}
		if (keyword) {
			params.keyword = keyword
		}
		return request('/api/academy/videos', 'GET', params)
	},
	
	// 获取视频详情
	getVideo(videoId) {
		return request(`/api/academy/videos/${videoId}`, 'GET')
	},
	
	// 获取个性化训练计划
	getPersonalPlan() {
		return requestWithToken('/api/academy/personal-plan', 'GET')
	},
	
	// 获取挑战任务列表
	getChallenges(limit = 10) {
		return request('/api/academy/challenges', 'GET', { limit })
	},
	
	// 获取今日挑战任务
	getDailyChallenges() {
		return requestWithToken('/api/academy/challenges/daily', 'GET')
	},
	
	// 完成挑战任务
	completeChallenge(challengeId) {
		return requestWithToken(`/api/academy/challenges/${challengeId}/complete`, 'POST')
	}
}

// 健康营养相关API
export const healthAPI = {
	// 获取营养指南列表
	getNutritionGuides() {
		return request('/api/health/nutrition-guides', 'GET')
	},
	
	// 获取营养指南详情
	getNutritionGuide(guideId) {
		return request(`/api/health/nutrition-guides/${guideId}`, 'GET')
	},
	
	// 获取睡眠数据
	getSleepData(targetDate) {
		const params = targetDate ? { target_date: targetDate } : {}
		return requestWithToken('/api/health/sleep-data', 'GET', params)
	},
	
	// 获取睡眠小贴士
	getSleepTips() {
		return request('/api/health/sleep-tips', 'GET')
	},
	
	// 获取运动损伤预防与康复列表
	getInjuryPrevention() {
		return requestWithToken('/api/health/injury-prevention', 'GET')
	},
	
	// 收藏/取消收藏运动损伤预防内容
	toggleCollect(injuryId) {
		return requestWithToken(`/api/health/injury-prevention/${injuryId}/collect`, 'POST')
	},
	
	// 获取健康监测数据
	getMonitorData(targetDate) {
		const params = targetDate ? { target_date: targetDate } : {}
		return requestWithToken('/api/health/monitor-data', 'GET', params)
	},
	
	// 创建或更新健康监测数据（模拟连接设备）
	createMonitorData(data) {
		return requestWithToken('/api/health/monitor-data', 'POST', data)
	}
}

// 默认导出（保持向后兼容）
export default {
	request,
	requestWithToken,
	authAPI,
	profileAPI,
	trainingAPI,
	matchAPI,
	communityAPI,
	academyAPI,
	healthAPI
}

