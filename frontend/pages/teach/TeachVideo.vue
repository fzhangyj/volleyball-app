<template>
	<view class="teach-video-container">
		<view class="video-wrapper">
			<video 
				class="video-player"
				:src="videoUrl"
				controls
				:poster="poster"
				:show-center-play-btn="true"
			></video>
		</view>
		<view class="video-info">
			<text class="video-title">{{ courseTitle }}</text>
			<view class="video-actions">
				<button class="add-plan-btn" @click="addToPlan">加入学习计划</button>
			</view>
		</view>
	</view>
</template>

<script>
	import { courseAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				courseId: null,
				courseTitle: '',
				videoUrl: '',
				poster: '/static/image/1.jpg'
			}
		},
		onLoad(options) {
			try {
				this.courseId = options.courseId ? parseInt(options.courseId) : null;
				this.courseTitle = options.title ? decodeURIComponent(options.title) : '视频课程';
				this.videoUrl = options.videoUrl ? decodeURIComponent(options.videoUrl) : '';
				
				// 如果有courseId但没有视频URL，从后端获取课程详情
				if (this.courseId && !this.videoUrl) {
					this.loadCourseDetail();
				}
			} catch (e) {
				console.error('解析参数失败:', e);
				this.courseTitle = '视频课程';
				this.videoUrl = '';
			}
		},
		methods: {
			// 从后端加载课程详情
			async loadCourseDetail() {
				try {
					const course = await courseAPI.getCourseDetail(this.courseId);
					if (course) {
						this.courseTitle = course.title || this.courseTitle;
						this.videoUrl = course.video_url || '';
						this.poster = course.cover_image || this.poster;
					}
				} catch (error) {
					console.error('加载课程详情失败:', error);
				}
			},
			
			// 加入学习计划
			async addToPlan() {
				// 检查登录状态
				const token = uni.getStorageSync('token');
				if (!token) {
					uni.showToast({
						title: '请先登录',
						icon: 'none',
						duration: 2000
					});
					return;
				}
				
				// 如果有courseId，调用后端API
				if (this.courseId) {
					try {
						await courseAPI.addFavorite({
							course_id: this.courseId,
							is_favorite: false,
							is_studying: true
						});
						uni.showToast({
							title: '已加入学习计划',
							icon: 'success',
							duration: 2000
						});
					} catch (error) {
						uni.showToast({
							title: error.message || '操作失败，请重试',
							icon: 'none',
							duration: 2000
						});
					}
				} else {
					// 没有courseId，提示用户
					uni.showToast({
						title: '该视频暂不支持加入学习计划',
						icon: 'none',
						duration: 2000
					});
				}
			}
		}
	}
</script>

<style scoped>
	.teach-video-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
	}

	.video-wrapper {
		width: 100%;
		height: 422rpx;
		background: #000000;
		position: relative;
		box-shadow: var(--shadow-card);
	}

	.video-player {
		width: 100%;
		height: 100%;
	}

	.video-info {
		padding: 40rpx 35rpx;
		background: var(--color-bg);
		min-height: calc(100vh - 422rpx);
	}

	.video-title {
		font-size: 38rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 40rpx;
		letter-spacing: 0.5rpx;
		line-height: 1.5;
		padding: 30rpx;
		background: var(--color-surface);
		border-radius: 24rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.video-actions {
		display: flex;
		justify-content: center;
		margin-top: 40rpx;
	}

	.add-plan-btn {
		background: var(--color-accent);
		color: #ffffff;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx 70rpx;
		font-size: 30rpx;
		font-weight: 700;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		letter-spacing: 0.5rpx;
	}

	.add-plan-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}
</style>

