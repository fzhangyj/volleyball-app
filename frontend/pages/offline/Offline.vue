<template>
	<view class="offline-container">
        <view class="page-heading"><text class="page-kicker">MEET ON COURT</text><text class="page-title">走上球场，一起进步。</text><text class="page-subtitle">发现身边的课程，把练习变成真实的相遇。</text></view>
		<!-- 搜索筛选栏 -->
		<view class="search-bar">
			<input 
				class="search-input" 
				type="text" 
				placeholder="搜索课程..." 
				v-model="searchKeyword"
				@input="filterCourses"
			/>
			<view class="filter-tabs">
				<view 
					class="filter-tab" 
					:class="{ active: currentFilter === 'all' }"
					@click="setFilter('all')"
				>全部</view>
				<view 
					class="filter-tab" 
					:class="{ active: currentFilter === 'area' }"
					@click="setFilter('area')"
				>按地区</view>
				<view 
					class="filter-tab" 
					:class="{ active: currentFilter === 'time' }"
					@click="setFilter('time')"
				>按时间</view>
			</view>
		</view>

		<view v-if="loading"><view class="ui-skeleton" /><view class="ui-skeleton" /></view>
        <view class="ui-state" v-else-if="!filteredCourses.length"><image class="ui-state-icon" src="/static/icons/map-pin-muted.png" /><text class="ui-state-title">{{ loadError ? '课程暂时没加载出来' : searchKeyword ? '还没有找到匹配的课程' : '新的球场相遇，正在准备' }}</text><text class="ui-state-desc">{{ loadError ? '请检查网络连接后重试。' : searchKeyword ? '试试其他课程名称或地区。' : '暂时没有线下课程，稍后再来看看吧。' }}</text><button v-if="loadError" class="ui-state-action" @click="loadCourses">重新加载</button></view>
        <!-- 课程卡片瀑布流 -->
		<view class="course-list" v-if="!loading">
			<view 
				class="course-card" 
				v-for="(course, index) in filteredCourses" 
				:key="index"
				@click="showCourseDetail(course)"
			>
				<image class="course-image" :src="course.image" mode="aspectFill"></image>
				<view class="course-info">
					<text class="course-title">{{ course.title }}</text>
					<text class="course-location">地点 · {{ course.location }}</text>
					<text class="course-time">时间 · {{ course.time }}</text>
					<text class="course-price">¥{{ course.price }}</text>
				</view>
			</view>
		</view>

		<!-- 课程详情弹窗 -->
		<view class="detail-modal" v-if="showDetail" @click="closeDetail">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">{{ selectedCourse.title }}</text>
					<text class="modal-close" @click="closeDetail">×</text>
				</view>
				<image class="modal-image" :src="selectedCourse.image" mode="widthFix"></image>
				<view class="modal-info">
					<text class="modal-text">地点 · 地点：{{ selectedCourse.location }}</text>
					<text class="modal-text">时间 · 时间：{{ selectedCourse.time }}</text>
					<text class="modal-text">人数：{{ selectedCourse.participants }}/{{ selectedCourse.maxParticipants }}</text>
					<text class="modal-text">价格：¥{{ selectedCourse.price }}</text>
					<text class="modal-desc">{{ selectedCourse.desc }}</text>
				</view>
				<button class="enroll-btn" @click="enrollCourse">立即报名</button>
			</view>
		</view>
	</view>
</template>

<script>
	import { offlineCourseAPI } from '@/utils/api.js'
    import { resolveMediaUrl } from '@/utils/config.js'
	
	export default {
		data() {
			return {
				searchKeyword: '',
				currentFilter: 'all',
				showDetail: false,
				selectedCourse: {},
				courseList: [],
				loading: false,
                loadError: false
			}
		},
		onLoad() {
			this.loadCourses()
		},
		computed: {
			filteredCourses() {
				let courses = this.courseList;
				
				// 搜索筛选
				if (this.searchKeyword) {
					courses = courses.filter(course => 
						course.title.includes(this.searchKeyword) ||
						course.location.includes(this.searchKeyword)
					);
				}
				
				// 其他筛选逻辑可以在这里添加
				return courses;
			}
		},
		methods: {
			async loadCourses() {
				this.loading = true
                this.loadError = false
				try {
					const params = {}
					if (this.searchKeyword) {
						params.search = this.searchKeyword
					}
					if (this.currentFilter === 'area') {
						// 可以添加地区筛选
					}
					
					const res = await offlineCourseAPI.getOfflineCourses(params)
					if (res && res.courses) {
						this.courseList = res.courses.map(course => ({
							id: course.id,
							title: course.title,
							location: course.location,
							time: course.schedule_info || '',
							price: course.price,
							participants: course.current_participants,
							maxParticipants: course.max_participants,
							image: resolveMediaUrl(course.image_url) || '/static/banners/volley-2.jpg',
							desc: course.description || ''
						}))
					}
				} catch (error) {
					console.error('加载线下课程失败:', error)
                    this.loadError = true
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			filterCourses() {
				// 搜索时重新加载数据
				this.loadCourses()
			},
			setFilter(filter) {
				this.currentFilter = filter;
				// 重新加载数据
				this.loadCourses()
			},
			async showCourseDetail(course) {
				try {
					// 获取课程详情
					const detail = await offlineCourseAPI.getOfflineCourseDetail(course.id)
					this.selectedCourse = {
						...course,
						desc: detail.description || course.desc
					}
					this.showDetail = true
				} catch (error) {
					console.error('加载课程详情失败:', error)
					this.selectedCourse = course
					this.showDetail = true
				}
			},
			closeDetail() {
				this.showDetail = false;
			},
			async enrollCourse() {
				try {
					const token = uni.getStorageSync('token')
					if (!token) {
						uni.showToast({
							title: '请先登录',
							icon: 'none'
						})
						setTimeout(() => {
							uni.navigateTo({
								url: '/pages/auth/Login'
							})
						}, 1500)
						return
					}
					
					await offlineCourseAPI.enrollOfflineCourse(this.selectedCourse.id, {
						contact_phone: ''
					})
					
					uni.showToast({
						title: '报名成功！',
						icon: 'success',
						duration: 2000
					});
					
					// 重新加载课程列表以更新参与人数
					this.loadCourses()
					
					setTimeout(() => {
						this.closeDetail();
					}, 2000);
				} catch (error) {
					console.error('报名失败:', error)
					uni.showToast({
						title: error.message || '报名失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			}
		}
	}
</script>

<style scoped>
	.offline-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
		padding-bottom: 100rpx;
	}

	.search-bar {
		background: var(--color-surface);
		border-radius: 24rpx;
		padding: 24rpx;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.search-input {
		width: 100%;
		height: 76rpx;
		background: var(--color-surface);
		border-radius: 38rpx;
		padding: 0 35rpx;
		font-size: 28rpx;
		margin-bottom: 24rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		transition: transform 160ms ease, background-color 160ms ease;
	}

	.search-input:focus {
		border-color: var(--color-line);
		box-shadow: var(--shadow-card);
	}

	.filter-tabs {
		display: flex;
		gap: 20rpx;
	}

	.filter-tab {
		flex: 1;
		text-align: center;
		padding: 18rpx;
		background: var(--color-surface);
		border-radius: 16rpx;
		font-size: 26rpx;
		color: var(--color-muted);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid transparent;
		font-weight: 500;
		box-shadow: var(--shadow-card);
	}

	.filter-tab.active {
		background: var(--color-accent);
		color: #ffffff;
		font-weight: 700;
		box-shadow: var(--shadow-card);
		transform: translateY(-2rpx);
		border-color: rgba(255, 255, 255, 0.3);
	}

	.course-list {
		display: flex;
		flex-direction: column;
		gap: 30rpx;
	}

	.course-card {
		background: var(--color-surface);
		border-radius: 24rpx;
		overflow: hidden;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 1rpx solid var(--color-line);
	}

	.course-card:active {
		transform: translateY(-4rpx) scale(0.98);
		box-shadow: var(--shadow-card);
	}

	.course-image {
		width: 100%;
		height: 320rpx;
		transition: transform 0.4s;
	}

	.course-card:active .course-image {
		transform: scale(1.05);
	}

	.course-info {
		padding: 30rpx;
	}

	.course-title {
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 18rpx;
		letter-spacing: 0.5rpx;
		line-height: 1.4;
	}

	.course-location,
	.course-time {
		font-size: 26rpx;
		color: var(--color-muted);
		display: block;
		margin-bottom: 12rpx;
		opacity: 0.85;
		line-height: 1.5;
	}

	.course-price {
		font-size: 40rpx;
		font-weight: 700;
		color: var(--color-accent);
		display: block;
		margin-top: 20rpx;
		letter-spacing: 0.5rpx;
		text-shadow: none;
	}

	.detail-modal {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(4rpx);
		animation: fadeIn 0.3s;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal-content {
		width: 90%;
		max-height: 80vh;
		background: var(--color-surface);
		border-radius: 28rpx;
		overflow-y: auto;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	@keyframes slideUp {
		from {
			transform: translateY(50rpx);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 35rpx;
		border-bottom: 2rpx solid var(--color-line);
		background: var(--color-surface);
	}

	.modal-title {
		font-size: 38rpx;
		font-weight: 700;
		color: var(--color-ink);
		letter-spacing: 0.5rpx;
	}

	.modal-close {
		font-size: 52rpx;
		color: var(--color-muted);
		line-height: 1;
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: transform 160ms ease, background-color 160ms ease;
	}

	.modal-close:active {
		background: rgba(0, 0, 0, 0.05);
		transform: rotate(90deg);
	}

	.modal-image {
		width: 100%;
		box-shadow: var(--shadow-card);
	}

	.modal-info {
		padding: 35rpx;
	}

	.modal-text {
		font-size: 28rpx;
		color: var(--color-muted);
		display: block;
		margin-bottom: 18rpx;
		line-height: 1.6;
		letter-spacing: 0.3rpx;
		padding: 12rpx 0;
		border-bottom: 1rpx solid var(--color-line);
	}

	.modal-text:last-of-type {
		border-bottom: none;
	}

	.modal-desc {
		font-size: 28rpx;
		color: var(--color-muted);
		line-height: 1.8;
		display: block;
		margin-top: 24rpx;
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 16rpx;
		border: 1rpx solid var(--color-line);
		letter-spacing: 0.3rpx;
	}

	.enroll-btn {
		width: 90%;
		margin: 35rpx auto;
		background: var(--color-accent);
		color: #ffffff;
		border: none;
		border-radius: 50rpx;
		padding: 28rpx;
		font-size: 32rpx;
		font-weight: 700;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		letter-spacing: 0.5rpx;
	}

	.enroll-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

.offline-container { padding: 40rpx 36rpx; }
.search-bar { padding: 0; background: transparent; border: none; box-shadow: none; margin-bottom: 30rpx; }
.search-input { width: 100%; height: 92rpx; border-radius: 18rpx; border: 1rpx solid #dce2d8; background: white; box-shadow: none; }
.filter-tabs { gap: 16rpx; }
.filter-tab { box-shadow: none; padding: 16rpx 20rpx; border-radius: 14rpx; background: #e9ede6; font-size: 25rpx; }
.filter-tab.active { background: var(--color-ink); color: white; transform: none; box-shadow: none; border-color: var(--color-ink); }
.course-card { box-shadow: none; border: 1rpx solid var(--color-line); }
.course-price { color: var(--color-accent); text-shadow: none; }
.modal-content { max-width: 620px; background: white; }
.enroll-btn { color: white; box-shadow: none; border-radius: 18rpx; padding: 18rpx; }
@media (min-width: 768px) { .course-list { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); } }

</style>

