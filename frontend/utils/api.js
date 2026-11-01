/**
 * API工具类：封装HTTP请求
 */
import { BASE_URL } from './config.js'

/**
 * 通用请求方法
 */
function request(url, method = 'GET', data = null, needAuth = false) {
	return new Promise((resolve, reject) => {
		// 构建请求头
		const header = {
			'Content-Type': 'application/json'
		}
		
		// 如果需要认证，添加token
		if (needAuth) {
			const token = uni.getStorageSync('token')
			if (token) {
				header['Authorization'] = `Bearer ${token}`
			}
		}
		
		// 发送请求
		uni.request({
			url: BASE_URL + url,
			method: method,
			data: data,
			header: header,
			success: (res) => {
				if (res.statusCode === 200 || res.statusCode === 201) {
					resolve(res.data)
				} else if (res.statusCode === 401) {
					// token过期，清除本地存储并跳转到登录页
					uni.removeStorageSync('token')
					uni.removeStorageSync('userInfo')
					uni.reLaunch({
						url: '/pages/auth/Login'
					})
					reject(new Error('登录已过期，请重新登录'))
				} else {
					reject(new Error(res.data.detail || '请求失败'))
				}
			},
			fail: (err) => {
				reject(new Error('网络请求失败：' + err.errMsg))
			}
		})
	})
}

/**
 * 认证相关API
 */
export const authAPI = {
	// 注册
	register(data) {
		return request('/auth/register', 'POST', data)
	},
	
	// 登录（用户名密码）
	login(data) {
		return request('/auth/login', 'POST', data)
	},
	
	// 发送短信验证码
	sendSmsCode(phone, scene = 'register') {
		return request('/auth/send-sms-code', 'POST', { phone, scene })
	},
	
	// 短信验证码登录
	smsLogin(data) {
		return request('/auth/sms-login', 'POST', data)
	},
	
	// 带验证码的注册
	registerWithSms(data) {
		return request('/auth/register-with-sms', 'POST', data)
	},
	
	// 使用验证码重置密码
	resetPasswordWithSms(data) {
		return request('/auth/reset-password-with-sms', 'POST', data)
	},
	
	// 忘记密码
	forgotPassword(data) {
		return request('/auth/forgot-password', 'POST', data)
	},
	
	// 重置密码
	resetPassword(data) {
		return request('/auth/reset-password', 'POST', data)
	},
	
	// 获取当前用户信息
	getCurrentUser() {
		return request('/auth/me', 'GET', null, true)
	},
	
	// 更新用户资料
	updateProfile(data) {
		return request('/auth/me', 'PUT', data, true)
	},
	
	// 上传头像
	uploadAvatar(filePath) {
		return new Promise((resolve, reject) => {
			uni.uploadFile({
				url: BASE_URL + '/auth/me/avatar',
				filePath: filePath,
				name: 'file',
				header: {
					'Authorization': `Bearer ${uni.getStorageSync('token')}`
				},
				success: (res) => {
					if (res.statusCode === 200) {
						try {
							const data = JSON.parse(res.data)
							resolve(data)
						} catch (e) {
							reject(new Error('解析响应失败'))
						}
					} else if (res.statusCode === 401) {
						uni.removeStorageSync('token')
						uni.removeStorageSync('userInfo')
						uni.reLaunch({
							url: '/pages/auth/Login'
						})
						reject(new Error('登录已过期，请重新登录'))
					} else {
						try {
							const error = JSON.parse(res.data)
							reject(new Error(error.detail || '上传失败'))
						} catch (e) {
							reject(new Error('上传失败'))
						}
					}
				},
				fail: (err) => {
					reject(new Error('网络请求失败：' + err.errMsg))
				}
			})
		})
	}
}

/**
 * 课程相关API
 */
export const courseAPI = {
	// 获取课程列表
	getCourses(params = {}) {
		const queryString = Object.keys(params)
			.map(key => `${key}=${encodeURIComponent(params[key])}`)
			.join('&')
		return request(`/courses/?${queryString}`, 'GET', null, false)
	},
	
	// 获取课程详情
	getCourseDetail(courseId) {
		return request(`/courses/${courseId}`, 'GET', null, false)
	},
	
	// 获取课程分类列表
	getCategories() {
		return request('/courses/categories/list', 'GET', null, false)
	},
	
	// 获取技能类型列表
	getSkillTypes() {
		return request('/courses/skills/list', 'GET', null, false)
	},
	
	// 获取技能详情
	getSkillDetail(skillType) {
		return request(`/courses/skills/${encodeURIComponent(skillType)}/detail`, 'GET', null, false)
	},
	
	// 收藏课程
	addFavorite(data) {
		return request('/courses/favorites', 'POST', data, true)
	},
	
	// 获取收藏列表
	getFavorites() {
		return request('/courses/favorites/list', 'GET', null, true)
	},
	
	// 取消收藏
	removeFavorite(courseId) {
		return request(`/courses/favorites/${courseId}`, 'DELETE', null, true)
	},
	
	// 获取学习中的课程
	getStudyingCourses() {
		return request('/courses/studying/list', 'GET', null, true)
	},
	
	// 创建或更新学习进度
	updateProgress(data) {
		return request('/courses/progress', 'POST', data, true)
	},
	
	// 获取学习进度列表
	getProgressList(skillType = null) {
		const url = skillType 
			? `/courses/progress/list?skill_type=${encodeURIComponent(skillType)}`
			: '/courses/progress/list'
		return request(url, 'GET', null, true)
	},
	
	// 获取学习统计
	getStatistics() {
		return request('/courses/statistics', 'GET', null, true)
	}
}

/**
 * Banner相关API
 */
export const bannerAPI = {
	// 获取Banner列表
	getBanners() {
		return request('/banners/', 'GET', null, false)
	},
	
	// 获取Banner详情
	getBannerDetail(bannerId) {
		return request(`/banners/${bannerId}`, 'GET', null, false)
	}
}

/**
 * 规则内容相关API
 */
export const ruleAPI = {
	// 获取规则内容
	getRuleContent() {
		return request('/rules/content', 'GET', null, false)
	},
	
	// 保存规则学习进度
	saveRuleProgress(data) {
		return request('/rules/progress', 'POST', data, true)
	}
}

/**
 * 训练相关API
 */
export const trainingAPI = {
	// 保存反应力训练记录
	saveReactionRecord(data) {
		return request('/training/reaction/record', 'POST', data, true)
	},
	
	// 获取训练记录
	getReactionRecords(gameMode = null, limit = 20) {
		const params = gameMode ? `?game_mode=${gameMode}&limit=${limit}` : `?limit=${limit}`
		return request(`/training/reaction/records${params}`, 'GET', null, true)
	},
	
	// 获取训练统计
	getReactionStatistics() {
		return request('/training/reaction/statistics', 'GET', null, true)
	}
}

/**
 * 线下课程相关API
 */
export const offlineCourseAPI = {
	// 获取线下课程列表
	getOfflineCourses(params = {}) {
		const queryString = Object.keys(params)
			.map(key => `${key}=${encodeURIComponent(params[key])}`)
			.join('&')
		return request(`/offline-courses/?${queryString}`, 'GET', null, false)
	},
	
	// 获取线下课程详情
	getOfflineCourseDetail(courseId) {
		return request(`/offline-courses/${courseId}`, 'GET', null, false)
	},
	
	// 报名线下课程
	enrollOfflineCourse(courseId, data) {
		return request(`/offline-courses/${courseId}/enroll`, 'POST', data, true)
	},
	
	// 获取我的报名列表
	getMyEnrollments() {
		return request('/offline-courses/my-enrollments/list', 'GET', null, true)
	}
}

/**
 * AI教练相关API
 */
export const aiAPI = {
	// 获取预设问题
	getPresetQuestions() {
		return request('/ai/preset-questions', 'GET', null, false)
	},
	
	// 与AI教练对话
	chat(data) {
		return request('/ai/chat', 'POST', data, true)
	},
	
	// 动作分析
	analyzeAction(data) {
		return request('/ai/analyze-action', 'POST', data, true)
	},
	
	// 快速问答（不保存历史）
	quickAnswer(data) {
		return request('/ai/quick-answer', 'POST', data, false)
	},
	
	// 获取会话列表
	getSessions(limit = 20, offset = 0) {
		return request(`/ai/sessions?limit=${limit}&offset=${offset}`, 'GET', null, true)
	},
	
	// 获取会话详情
	getSessionDetail(sessionId) {
		return request(`/ai/sessions/${sessionId}`, 'GET', null, true)
	},
	
	// 删除会话
	deleteSession(sessionId) {
		return request(`/ai/sessions/${sessionId}`, 'DELETE', null, true)
	}
}

export default {
	authAPI,
	courseAPI,
	bannerAPI,
	ruleAPI,
	trainingAPI,
	offlineCourseAPI,
	aiAPI
}

