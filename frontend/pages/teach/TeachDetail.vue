<template>
	<view class="teach-detail-container">
		<view class="detail-content" v-if="!loading">
			<view class="detail-header">
				<view class="detail-title">{{ skillTitle }}</view>
				<view class="detail-actions">
					<view class="action-btn" :class="{ active: isFavorite }" @click="toggleFavorite">
						<text class="action-icon">{{ isFavorite ? '❤️' : '🤍' }}</text>
						<text class="action-text">{{ isFavorite ? '已收藏' : '收藏' }}</text>
					</view>
					<view class="action-btn" :class="{ active: isStudying }" @click="addToStudyPlan" v-if="!isStudying">
						<text class="action-icon">📚</text>
						<text class="action-text">加入学习</text>
					</view>
				</view>
			</view>
			
			<!-- 学习进度条 -->
			<view class="progress-section" v-if="courseId && currentProgress > 0">
				<view class="progress-header">
					<text class="progress-label">学习进度</text>
					<text class="progress-value">{{ currentProgress }}%</text>
				</view>
				<view class="progress-bar">
					<view class="progress-fill" :style="{ width: currentProgress + '%' }"></view>
				</view>
			</view>
			
			<image 
				class="detail-image" 
				:src="courseData?.cover_image || '/static/image/1.jpg'" 
				mode="widthFix"
			></image>
			
			<view class="detail-intro">
				<text class="intro-title">技能概览</text>
				<text class="intro-text">{{ skillIntro }}</text>
				<view class="focus-points" v-if="focusPoints.length">
					<text class="focus-title">核心关注点</text>
					<view class="focus-chip" v-for="(point, index) in focusPoints" :key="index">
						{{ point }}
					</view>
				</view>
			</view>
			
			<view class="training-methods">
				<text class="methods-title">训练方法</text>
				<view class="method-item" v-for="(method, index) in trainingMethods" :key="index">
					<text class="method-number">{{ index + 1 }}</text>
					<view class="method-content">
						<text class="method-title">{{ method.title }}</text>
						<text class="method-desc">{{ method.desc }}</text>
					</view>
				</view>
			</view>

			<view class="tips-section">
				<text class="tips-title">注意事项</text>
				<text class="tips-text" v-for="(tip, index) in tips" :key="index">• {{ tip }}</text>
			</view>
			
			<!-- 学习完成按钮 -->
			<view class="complete-section" v-if="courseId && currentProgress < 100">
				<button class="complete-btn" @click="markComplete">标记为已完成</button>
			</view>
		</view>
		
		<!-- 加载中 -->
		<view class="loading-container" v-if="loading">
			<text class="loading-text">加载中...</text>
		</view>
	</view>
</template>

<script>
	import { courseAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loading: false,
				courseId: null,
				courseData: null,
				skillTitle: '技能详情',
				skillIntro: '',
				trainingMethods: [],
				tips: [],
				focusPoints: [],
				isFavorite: false,
				isStudying: false,
				currentProgress: 0
			}
		},
		onLoad(options) {
			this.loading = true
			try {
				// 优先从courseId获取课程数据
				if (options.courseId) {
					this.courseId = parseInt(options.courseId)
					this.loadCourseData(this.courseId)
				} else if (options.skill) {
					// 兼容旧的skill参数
					this.skillTitle = decodeURIComponent(options.skill)
					this.loadSkillData(this.skillTitle)
				}
			} catch (e) {
				console.error('加载数据失败:', e)
				uni.showToast({
					title: '加载失败，请重试',
					icon: 'none',
					duration: 2000
				})
				this.loading = false
			}
		},
		methods: {
			// 从后端加载课程数据
			async loadCourseData(courseId) {
				try {
					const course = await courseAPI.getCourseDetail(courseId)
					if (course) {
						this.courseData = course
						this.skillTitle = course.title
						this.skillIntro = course.description || course.content || ''
						
						// 如果有视频，添加视频相关的方法
						if (course.video_url) {
							this.trainingMethods.push({
								title: '视频学习',
								desc: '观看专业教学视频，学习正确的动作要领'
							})
						}
						
						// 加载用户相关状态
						await this.loadUserCourseStatus(courseId)
						await this.loadProgress(courseId)
						
						// 如果课程有技能类型，加载技能相关数据
						if (course.skill_type) {
							this.loadSkillData(course.skill_type)
						}
					}
				} catch (error) {
					console.error('加载课程数据失败:', error)
					uni.showToast({
						title: '加载课程失败',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			
			// 加载用户课程状态（收藏、学习中）
			async loadUserCourseStatus(courseId) {
				try {
					const favorites = await courseAPI.getFavorites()
					const studying = await courseAPI.getStudyingCourses()
					
					this.isFavorite = favorites.some(item => item.course_id === courseId)
					this.isStudying = studying.some(item => item.course_id === courseId)
				} catch (error) {
					console.error('加载用户状态失败:', error)
				}
			},
			
			// 加载学习进度
			async loadProgress(courseId) {
				try {
					const progresses = await courseAPI.getProgressList()
					const progress = progresses.find(p => p.course_id === courseId)
					if (progress) {
						this.currentProgress = progress.progress || 0
					}
				} catch (error) {
					console.error('加载进度失败:', error)
				}
			},
			
			// 收藏/取消收藏
			async toggleFavorite() {
				try {
					if (this.isFavorite) {
						await courseAPI.removeFavorite(this.courseId)
						this.isFavorite = false
						uni.showToast({
							title: '已取消收藏',
							icon: 'success'
						})
					} else {
						await courseAPI.addFavorite({
							course_id: this.courseId,
							is_favorite: true,
							is_studying: this.isStudying
						})
						this.isFavorite = true
						uni.showToast({
							title: '已收藏',
							icon: 'success'
						})
					}
				} catch (error) {
					uni.showToast({
						title: error.message || '操作失败',
						icon: 'none'
					})
				}
			},
			
			// 加入学习计划
			async addToStudyPlan() {
				try {
					await courseAPI.addFavorite({
						course_id: this.courseId,
						is_favorite: this.isFavorite,
						is_studying: true
					})
					this.isStudying = true
					uni.showToast({
						title: '已加入学习计划',
						icon: 'success'
					})
				} catch (error) {
					uni.showToast({
						title: error.message || '操作失败',
						icon: 'none'
					})
				}
			},
			
			// 更新学习进度
			async updateProgress(progress) {
				try {
					await courseAPI.updateProgress({
						course_id: this.courseId,
						skill_type: this.courseData?.skill_type,
						progress: progress,
						study_duration: 1 // 每次学习1分钟
					})
					this.currentProgress = progress
				} catch (error) {
					console.error('更新进度失败:', error)
				}
			},
			
			// 从后端加载技能详情数据
			async loadSkillData(skill) {
				try {
					const skillDetail = await courseAPI.getSkillDetail(skill)
					
					if (skillDetail) {
						// 设置技能介绍
						if (skillDetail.intro) {
							this.skillIntro = skillDetail.intro
						} else if (!this.skillIntro) {
							this.skillIntro = skillDetail.description || '排球的每一项技能都依赖扎实的基本功与全身协同。学习时要先建立正确动作图像，再通过低强度、高重复的练习把细节刻进身体记忆，最后才是加速、加力量的阶段。'
						}
						
						// 设置核心关注点
						if (skillDetail.focusPoints && Array.isArray(skillDetail.focusPoints)) {
							this.focusPoints = skillDetail.focusPoints
						}
						
						// 设置训练方法（合并，不覆盖已有的）
						if (skillDetail.trainingMethods && Array.isArray(skillDetail.trainingMethods)) {
							if (this.trainingMethods.length === 0) {
								this.trainingMethods = skillDetail.trainingMethods
							} else {
								this.trainingMethods = [...this.trainingMethods, ...skillDetail.trainingMethods]
							}
						}
						
						// 设置注意事项
						if (skillDetail.tips && Array.isArray(skillDetail.tips)) {
							this.tips = skillDetail.tips
						}
					}
				} catch (error) {
					console.error('加载技能详情失败:', error)
					// 加载失败时使用默认文本
					if (!this.skillIntro) {
						this.skillIntro = '排球的每一项技能都依赖扎实的基本功与全身协同。学习时要先建立正确动作图像，再通过低强度、高重复的练习把细节刻进身体记忆，最后才是加速、加力量的阶段。'
					}
				}
			},
			
			// 标记为已完成
			async markComplete() {
				try {
					await this.updateProgress(100)
					uni.showToast({
						title: '恭喜完成学习！',
						icon: 'success'
					})
				} catch (error) {
					uni.showToast({
						title: '操作失败',
						icon: 'none'
					})
				}
			}
		}
	}
</script>

<style scoped>
	.teach-detail-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
	}

	.detail-content {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 45rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.detail-title {
		font-size: 44rpx;
		font-weight: 700;
		color: var(--color-ink);
		text-align: center;
		margin-bottom: 35rpx;
		letter-spacing: 1rpx;
		position: relative;
		padding-bottom: 20rpx;
	}

	.detail-title::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 80rpx;
		height: 4rpx;
		background: var(--color-accent);
		border-radius: 2rpx;
	}

	.detail-image {
		width: 100%;
		border-radius: 20rpx;
		margin-bottom: 45rpx;
		box-shadow: var(--shadow-card);
	}

	.detail-intro {
		background: linear-gradient(135deg, #FFF8E1 0%, #FFE8B8 100%);
		border-radius: 20rpx;
		padding: 35rpx;
		margin-bottom: 45rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.intro-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #D48806;
		margin-bottom: 20rpx;
		display: block;
		letter-spacing: 0.5rpx;
	}

	.intro-text {
		font-size: 28rpx;
		color: #5F4B32;
		line-height: 1.8;
		display: block;
		letter-spacing: 0.3rpx;
	}

	.focus-points {
		margin-top: 28rpx;
	}

	.focus-title {
		font-size: 30rpx;
		color: #8C6E3D;
		margin-bottom: 16rpx;
		display: block;
		font-weight: 600;
	}

	.focus-chip {
		display: inline-flex;
		align-items: center;
		padding: 12rpx 24rpx;
		background: var(--color-surface);
		border-radius: 30rpx;
		font-size: 26rpx;
		color: #8C6E3D;
		margin-right: 16rpx;
		margin-bottom: 16rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		font-weight: 500;
	}

	.training-methods {
		margin-bottom: 45rpx;
	}

	.methods-title,
	.tips-title {
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 28rpx;
		letter-spacing: 0.5rpx;
		position: relative;
		padding-left: 20rpx;
	}

	.methods-title::before,
	.tips-title::before {
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

	.method-item {
		display: flex;
		margin-bottom: 32rpx;
		align-items: flex-start;
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 20rpx;
		border: 1rpx solid var(--color-line);
		transition: transform 160ms ease, background-color 160ms ease;
	}

	.method-item:active {
		transform: translateX(4rpx);
		box-shadow: var(--shadow-card);
	}

	.method-number {
		width: 56rpx;
		height: 56rpx;
		background: var(--color-accent);
		color: #ffffff;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 26rpx;
		font-weight: 700;
		margin-right: 24rpx;
		flex-shrink: 0;
		box-shadow: var(--shadow-card);
		border: 2rpx solid rgba(255, 255, 255, 0.3);
	}

	.method-content {
		flex: 1;
	}

	.method-title {
		font-size: 30rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 12rpx;
		letter-spacing: 0.3rpx;
	}

	.method-desc {
		font-size: 28rpx;
		color: var(--color-muted);
		line-height: 1.7;
		letter-spacing: 0.3rpx;
	}

	.tips-section {
		padding-top: 35rpx;
		border-top: 2rpx solid var(--color-line);
	}

	.tips-text {
		font-size: 28rpx;
		color: var(--color-muted);
		line-height: 1.9;
		display: block;
		margin-bottom: 18rpx;
		padding-left: 12rpx;
		letter-spacing: 0.3rpx;
		position: relative;
	}

	.tips-text::before {
		content: '';
		position: absolute;
		left: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 6rpx;
		height: 6rpx;
		background: var(--color-accent);
		border-radius: 50%;
	}
	
	.detail-header {
		margin-bottom: 30rpx;
	}
	
	.detail-actions {
		display: flex;
		gap: 20rpx;
		margin-top: 20rpx;
		justify-content: center;
	}
	
	.action-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 20rpx 30rpx;
		background: var(--color-surface);
		border-radius: 16rpx;
		border: 2rpx solid var(--color-line);
		transition: transform 160ms ease, background-color 160ms ease;
	}
	
	.action-btn.active {
		background: var(--color-accent);
		border-color: var(--color-accent);
	}
	
	.action-icon {
		font-size: 36rpx;
		margin-bottom: 8rpx;
	}
	
	.action-text {
		font-size: 24rpx;
		color: var(--color-ink);
		font-weight: 600;
	}
	
	.progress-section {
		margin-bottom: 30rpx;
		padding: 30rpx;
		background: var(--color-surface);
		border-radius: 20rpx;
		border: 1rpx solid var(--color-line);
	}
	
	.progress-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}
	
	.progress-label {
		font-size: 28rpx;
		color: var(--color-ink);
		font-weight: 600;
	}
	
	.progress-value {
		font-size: 32rpx;
		color: var(--color-accent);
		font-weight: 700;
	}
	
	.progress-bar {
		width: 100%;
		height: 16rpx;
		background: rgba(245, 245, 245, 0.8);
		border-radius: 8rpx;
		overflow: hidden;
	}
	
	.progress-fill {
		height: 100%;
		background: var(--color-accent);
		border-radius: 8rpx;
		transition: width 0.6s;
	}
	
	.complete-section {
		margin-top: 50rpx;
		padding-top: 40rpx;
		border-top: 2rpx solid var(--color-line);
	}
	
	.complete-btn {
		width: 100%;
		height: 88rpx;
		background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
		border-radius: 16rpx;
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: 700;
		border: none;
		box-shadow: var(--shadow-card);
	}
	
	.complete-btn::after {
		border: none;
	}
	
	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 400rpx;
	}
	
	.loading-text {
		font-size: 28rpx;
		color: var(--color-muted);
	}

.detail-title { font-size: 42rpx; }
.action-btn { box-shadow: none; border-radius: 14rpx; }
.action-btn.active { background: var(--color-accent-soft); border-color: #e6c5b7; }
.action-btn.active .action-text { color: var(--color-accent); }
.focus-chip { background: var(--color-accent-soft); color: var(--color-accent); border: none; box-shadow: none; }
.method-number { color: white; box-shadow: none; }
.detail-intro, .training-methods, .tips-section { box-shadow: none; }
.complete-btn { background: var(--color-accent); color: white; border-radius: 18rpx; box-shadow: none; }

</style>

