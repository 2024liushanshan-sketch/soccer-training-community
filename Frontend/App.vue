<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 延迟检查登录状态，确保页面已加载
			setTimeout(() => {
				this.checkLogin()
			}, 500)
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			checkLogin() {
				// 在H5环境下，登录检查由各个页面自己处理
				// #ifdef H5
				console.log('H5环境，跳过全局登录检查')
				return
				// #endif
				
				const token = uni.getStorageSync('token')
				if (!token) {
					// 获取当前页面路由
					try {
						const pages = getCurrentPages()
						if (pages && pages.length > 0) {
							const currentPage = pages[pages.length - 1]
							const route = currentPage ? currentPage.route : ''
							// 如果不在登录相关页面，跳转到登录页
							if (route && !route.includes('auth/')) {
								setTimeout(() => {
									uni.reLaunch({
										url: '/pages/auth/login'
									})
								}, 100)
							}
						}
					} catch (e) {
						// 如果获取页面失败，直接跳转
						setTimeout(() => {
							uni.reLaunch({
								url: '/pages/auth/login'
							})
						}, 100)
					}
				}
			}
		}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		background-color: #F5F5F5;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
	}
</style>
