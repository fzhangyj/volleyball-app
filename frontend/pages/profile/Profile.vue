<template>
	<view class="profile-container">
        <view class="page-heading"><text class="page-kicker">MY VOLLEYBALL JOURNEY</text><text class="page-title">每一点进步，都算数。</text></view>
		<!-- 用户信息区 -->
		<view class="user-section">
			<image 
				class="user-avatar"
                :class="{ 'avatar-placeholder': !avatarUrl }" 
				:src="avatarUrl || '/static/icons/ball-volleyball-active.png'" 
				mode="aspectFill"
			></image>
			<text class="user-name">{{ userName }}</text>
			<view class="user-actions">
				<button class="settings-btn" v-if="isLoggedIn" @click="goToSettings">设置</button>
				<button class="login-btn" v-if="!isLoggedIn" @click="goToLogin">点击登录</button>
				<button class="logout-btn" v-else @click="handleLogout">退出登录</button>
			</view>
		</view>
		
		<!-- 学习统计区 -->
		<view class="statistics-section" v-if="isLoggedIn">
			<text class="section-title">学习统计</text>
			<view class="statistics-grid">
				<view class="stat-item">
					<text class="stat-value">{{ Math.floor(statistics.total_study_time / 60) }}</text>
					<text class="stat-label">学习时长(小时)</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ statistics.completed_courses }}</text>
					<text class="stat-label">完成课程</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ statistics.studying_courses }}</text>
					<text class="stat-label">学习中</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ statistics.favorite_courses }}</text>
					<text class="stat-label">收藏</text>
				</view>
			</view>
		</view>

		<!-- 学习进度区 -->
		<view class="progress-section">
			<text class="section-title">学习进度</text>
			<text class="ui-state-desc" v-if="!skillProgress.length">还没有学习记录，完成一次练习就从这里开始。</text>
            <view class="progress-list">
				<view class="progress-item" v-for="(skill, index) in skillProgress" :key="index">
					<view class="progress-header">
						<text class="skill-name">{{ skill.name }}</text>
						<text class="progress-percent">{{ skill.progress }}%</text>
					</view>
					<view class="progress-bar">
						<view class="progress-fill" :style="{ width: skill.progress + '%' }"></view>
					</view>
					<text class="skill-detail" v-if="skill.detail">{{ skill.detail }}</text>
				</view>
			</view>
		</view>

		<!-- 已加入课程列表 -->
		<view class="course-section">
			<text class="section-title">已加入课程</text>
			<view class="course-list" v-if="studyPlan.length > 0">
				<view 
					class="course-item" 
					v-for="(course, index) in studyPlan" 
					:key="index"
					@click="goToCourseDetail(course)"
				>
					<image class="course-thumb" :src="course.coverImage || '/static/image/1.jpg'" mode="aspectFill"></image>
					<view class="course-info">
						<text class="course-title">{{ course.title }}</text>
						<text class="course-status">学习中</text>
					</view>
					<text class="course-arrow">></text>
				</view>
			</view>
			<view class="empty-course" v-else>
				<image class="ui-state-icon" src="/static/icons/book-muted.png" />
				<text class="empty-text">暂无课程，快去学习吧！</text>
				<text class="empty-hint">在课程页面加入学习计划，开始你的排球之旅</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { authAPI, courseAPI } from '@/utils/api.js'
	
	import { BASE_URL } from '@/utils/config.js'
	
	export default {
		data() {
			return {
				userName: '排球少年',
				userInfo: null,
				isLoggedIn: false,
				loading: false,
				avatarUrl: '',
				statistics: {
					total_study_time: 0,
					completed_courses: 0,
					studying_courses: 0,
					favorite_courses: 0
				},
				skillProgress: [],
				studyPlan: [],
				favoriteCourses: []
			}
		},
		onLoad() {
			this.checkLoginStatus();
			if (this.isLoggedIn) {
				this.loadData();
			}
		},
		onShow() {
			// 每次显示页面时重新加载数据
			this.checkLoginStatus();
			if (this.isLoggedIn) {
				this.loadData();
			}
		},
		methods: {
			async checkLoginStatus() {
				// 检查是否已登录
				const token = uni.getStorageSync('token');
				const userInfo = uni.getStorageSync('userInfo');
				
				if (token && userInfo) {
					this.isLoggedIn = true;
					this.userInfo = userInfo;
					this.userName = userInfo.username || '排球少年';
					
					// 加载头像
					if (userInfo.avatar) {
						this.avatarUrl = `${BASE_URL}/uploads/${userInfo.avatar}`;
					}
					
					// 从后端获取最新用户信息（包括头像）
					try {
						const latestUserInfo = await authAPI.getCurrentUser();
						if (latestUserInfo) {
							this.userInfo = latestUserInfo;
							this.userName = latestUserInfo.username || '排球少年';
							if (latestUserInfo.avatar) {
								this.avatarUrl = `${BASE_URL}/uploads/${latestUserInfo.avatar}`;
							} else {
								this.avatarUrl = '';
							}
							// 更新本地存储
							uni.setStorageSync('userInfo', latestUserInfo);
						}
					} catch (error) {
						console.error('获取用户信息失败:', error);
					}
				} else {
					this.isLoggedIn = false;
					this.userInfo = null;
					this.userName = '未登录';
					this.avatarUrl = '';
				}
			},
			
			goToLogin() {
				uni.navigateTo({
					url: '/pages/auth/Login'
				});
			},
			
			goToSettings() {
				uni.navigateTo({
					url: '/pages/profile/Settings'
				});
			},
			
			handleLogout() {
				uni.showModal({
					title: '提示',
					content: '确定要退出登录吗？',
					success: (res) => {
						if (res.confirm) {
							// 清除本地存储
							uni.removeStorageSync('token');
							uni.removeStorageSync('userInfo');
							
							// 更新状态
							this.isLoggedIn = false;
							this.userInfo = null;
							this.userName = '未登录';
							
							uni.showToast({
								title: '已退出登录',
								icon: 'success'
							});
						}
					}
				});
			},
			// 加载所有数据
			async loadData() {
				this.loading = true
				try {
					await Promise.all([
						this.loadStatistics(),
						this.loadStudyPlan(),
						this.loadProgress(),
						this.loadFavorites()
					])
				} catch (error) {
					console.error('加载数据失败:', error)
				} finally {
					this.loading = false
				}
			},
			
			// 加载学习统计
			async loadStatistics() {
				try {
					const res = await courseAPI.getStatistics()
					if (res) {
						this.statistics = {
							total_study_time: res.total_study_time || 0,
							completed_courses: res.completed_courses || 0,
							studying_courses: res.studying_courses || 0,
							favorite_courses: res.favorite_courses || 0
						}
					}
				} catch (error) {
					console.error('加载统计失败:', error)
				}
			},
			
			// 加载学习中的课程
			async loadStudyPlan() {
				try {
					const res = await courseAPI.getStudyingCourses()
					if (res && Array.isArray(res)) {
						this.studyPlan = res.map(item => ({
							id: item.course_id,
							title: item.course ? item.course.title : '未知课程',
							videoUrl: item.course ? item.course.video_url : null,
							coverImage: item.course ? item.course.cover_image : null
						}))
					} else {
						this.studyPlan = []
					}
				} catch (error) {
					console.error('加载学习计划失败:', error)
					this.studyPlan = []
				}
			},
			
			// 加载学习进度
			async loadProgress() {
				try {
					// 同时获取技能类型列表和用户进度
					const [skillTypes, progressList] = await Promise.all([
						courseAPI.getSkillTypes(),
						courseAPI.getProgressList()
					])
					
					// 创建进度映射
					const progressMap = {}
					if (progressList && Array.isArray(progressList)) {
						progressList.forEach(p => {
							if (p.skill_type) {
								progressMap[p.skill_type] = p.progress || 0
							}
						})
					}
					
					// 根据技能类型列表生成进度显示
					if (skillTypes && Array.isArray(skillTypes)) {
						this.skillProgress = skillTypes.map(skill => ({
							name: skill.name + '技巧',
							progress: progressMap[skill.skillType] || 0,
							skill_type: skill.skillType
						}))
					} else {
						this.skillProgress = []
					}
				} catch (error) {
					console.error('加载进度失败:', error)
					this.skillProgress = []
				}
			},
			
			// 加载收藏的课程
			async loadFavorites() {
				try {
					const res = await courseAPI.getFavorites()
					if (res && Array.isArray(res)) {
						this.favoriteCourses = res.map(item => ({
							id: item.course_id,
							title: item.course ? item.course.title : '未知课程',
							coverImage: item.course ? item.course.cover_image : null
						}))
					} else {
						this.favoriteCourses = []
					}
				} catch (error) {
					console.error('加载收藏失败:', error)
					this.favoriteCourses = []
				}
			},
			goToCourseDetail(course) {
				if (!course) return;
				try {
					// 跳转到课程详情页
					if (course.videoUrl) {
						uni.navigateTo({
							url: `/pages/teach/TeachVideo?title=${encodeURIComponent(course.title || '')}&videoUrl=${encodeURIComponent(course.videoUrl || '')}`
						});
					} else {
						uni.navigateTo({
							url: '/pages/teach/TeachDetail'
						});
					}
				} catch (e) {
					console.error('跳转失败:', e);
					uni.showToast({
						title: '跳转失败，请重试',
						icon: 'none',
						duration: 2000
					});
				}
			}
		}
	}
</script>

<style scoped>
	.profile-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
		padding-bottom: 100rpx;
	}

	.user-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 45rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.user-avatar {
		width: 160rpx;
		height: 160rpx;
		border-radius: 50%;
		margin-bottom: 24rpx;
		border: 5rpx solid;
		border-image: var(--color-accent) 1;
		box-shadow: var(--shadow-card);
	}

	.user-name {
		font-size: 38rpx;
		font-weight: 700;
		color: var(--color-ink);
		letter-spacing: 0.5rpx;
		margin-bottom: 20rpx;
	}
	
	.user-actions {
		display: flex;
		gap: 20rpx;
		margin-top: 30rpx;
	}
	
	.login-btn,
	.logout-btn,
	.settings-btn {
		height: 60rpx;
		line-height: 60rpx;
		border-radius: 30rpx;
		color: #FFFFFF;
		font-size: 26rpx;
		font-weight: 600;
		border: none;
		padding: 0 30rpx;
	}
	
	.login-btn::after,
	.logout-btn::after,
	.settings-btn::after {
		border: none;
	}
	
	.login-btn {
		background: var(--color-accent);
	}
	
	.settings-btn {
		background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
	}
	
	.logout-btn {
		background: linear-gradient(135deg, var(--color-accent) 0%, #FF5252 100%);
	}
	
	.statistics-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 35rpx;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}
	
	.statistics-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
		margin-top: 30rpx;
	}
	
	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 30rpx 20rpx;
		background: var(--color-surface);
		border-radius: 20rpx;
		border: 1rpx solid var(--color-line);
	}
	
	.stat-value {
		font-size: 48rpx;
		font-weight: 700;
		color: var(--color-accent);
		margin-bottom: 12rpx;
	}
	
	.stat-label {
		font-size: 24rpx;
		color: var(--color-muted);
	}

	.progress-section,
	.course-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 35rpx;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.section-title {
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 35rpx;
		letter-spacing: 0.5rpx;
		position: relative;
		padding-left: 20rpx;
	}

	.section-title::before {
		content: '';
		position: absolute;
		left: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 6rpx;
		height: 30rpx;
		background: var(--color-accent);
		border-radius: 3rpx;
	}

	.progress-list {
		display: flex;
		flex-direction: column;
		gap: 32rpx;
	}

	.progress-item {
		display: flex;
		flex-direction: column;
		gap: 14rpx;
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 20rpx;
		border: 1rpx solid var(--color-line);
	}

	.progress-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: 18rpx;
		align-items: center;
	}

	.skill-name {
		font-size: 30rpx;
		color: var(--color-ink);
		font-weight: 600;
		letter-spacing: 0.3rpx;
	}

	.progress-percent {
		font-size: 30rpx;
		color: var(--color-accent);
		font-weight: 700;
		letter-spacing: 0.5rpx;
	}

	.progress-bar {
		width: 100%;
		height: 14rpx;
		background: rgba(245, 245, 245, 0.8);
		border-radius: 7rpx;
		overflow: hidden;
		box-shadow: var(--shadow-card);
	}

	.progress-fill {
		height: 100%;
		background: var(--color-accent);
		border-radius: 7rpx;
		transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: var(--shadow-card);
		position: relative;
		overflow: hidden;
	}

	.progress-fill::after {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
		animation: none;
	}

	@keyframes shimmer {
		0% { left: -100%; }
		100% { left: 100%; }
	}

	.skill-detail {
		font-size: 26rpx;
		color: var(--color-muted);
		line-height: 1.5;
		padding-top: 8rpx;
		opacity: 0.85;
	}

	.course-list {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
	}

	.course-item {
		display: flex;
		align-items: center;
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 20rpx;
		transition: transform 160ms ease, background-color 160ms ease;
		border: 1rpx solid var(--color-line);
		box-shadow: var(--shadow-card);
	}

	.course-item:active {
		background: var(--color-surface);
		transform: translateY(-2rpx);
		box-shadow: var(--shadow-card);
	}

	.course-thumb {
		width: 130rpx;
		height: 130rpx;
		border-radius: 16rpx;
		margin-right: 24rpx;
		box-shadow: var(--shadow-card);
	}

	.course-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.course-title {
		font-size: 30rpx;
		color: var(--color-ink);
		margin-bottom: 12rpx;
		font-weight: 600;
		letter-spacing: 0.3rpx;
	}

	.course-status {
		font-size: 26rpx;
		color: var(--color-accent);
		font-weight: 500;
	}

	.course-arrow {
		font-size: 36rpx;
		color: var(--color-muted);
		font-weight: 300;
	}

	.empty-course {
		text-align: center;
		padding: 100rpx 40rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.empty-icon {
		font-size: 120rpx;
		margin-bottom: 30rpx;
		opacity: 0.6;
		animation: none;
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-20rpx);
		}
	}

	.empty-text {
		color: var(--color-muted);
		font-size: 32rpx;
		font-weight: 600;
		margin-bottom: 16rpx;
		opacity: 0.8;
	}

	.empty-hint {
		color: var(--color-muted);
		font-size: 26rpx;
		opacity: 0.7;
		line-height: 1.6;
	}

.profile-container { padding: 40rpx 36rpx; }
.user-section { align-items: flex-start; padding: 30rpx 30rpx 30rpx 150rpx; min-height: 180rpx; position: relative; border: 1rpx solid var(--color-line); background: #edf0e9; box-shadow: none; }
.user-avatar { position: absolute; left: 28rpx; top: 34rpx; width: 92rpx; height: 92rpx; border: 3rpx solid white; border-image: none; box-shadow: none; }
.user-name { font-size: 36rpx; margin: 0; overflow-wrap: anywhere; }
.user-actions { margin-top: 18rpx; gap: 12rpx; flex-wrap: wrap; }
.settings-btn, .logout-btn, .login-btn { height: 68rpx; line-height: 68rpx; padding: 0 24rpx; font-size: 23rpx; border-radius: 12rpx; margin: 0; }
.settings-btn, .login-btn { background: var(--color-ink); color: white; }
.logout-btn { background: transparent; color: var(--color-muted); }
.statistics-section, .progress-section, .course-section { padding: 28rpx; border: 1rpx solid var(--color-line); box-shadow: none; margin-bottom: 24rpx; border-radius: 24rpx; }
.section-title { padding-left: 0; margin-bottom: 24rpx; font-size: 31rpx; }
.section-title::before { display: none; }
.statistics-grid { grid-template-columns: repeat(4,minmax(0,1fr)); gap: 10rpx; margin-top: 20rpx; }
.stat-item { border: none; border-radius: 0; background: transparent; padding: 10rpx 0; }
.stat-value { color: var(--color-ink); font-size: 44rpx; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 20rpx; text-align: center; }
.progress-item { padding: 0; border: none; background: transparent; }
.progress-bar { height: 10rpx; box-shadow: none; }
.progress-fill { box-shadow: none; background: var(--color-accent); }
.progress-fill::after { display: none; }
.empty-course { padding: 38rpx 0; }
.empty-text { font-size: 27rpx; color: var(--color-ink); opacity: 1; }
.empty-hint { font-size: 23rpx; color: var(--color-muted); opacity: 1; }


.logo { background: var(--color-accent-soft); padding: 14rpx; }
.user-avatar { background: var(--color-accent-soft); }
.avatar-placeholder { padding: 14rpx; }
</style>

