<template>
	<view class="teach-course-container">
		<!-- 搜索栏 -->
		<view class="search-section">
			<view class="search-box">
				<input 
					class="search-input" 
					v-model="searchKeyword" 
					placeholder="搜索课程..."
					@confirm="handleSearch"
					@input="handleSearchInput"
				/>
				<button class="search-icon-button" aria-label="搜索课程" @click="handleSearch"><image class="ui-icon" src="/static/icons/search-muted.png" /></button>
			</view>
		</view>
		
		<!-- 分类筛选 -->
		<view class="filter-section">
			<scroll-view class="filter-scroll" scroll-x>
				<view 
					class="filter-item" 
					:class="{ active: selectedCategory === null }"
					@click="selectCategory(null)"
				>
					全部
				</view>
				<view 
					class="filter-item" 
					:class="{ active: selectedCategory === cat.id }"
					v-for="cat in categories" 
					:key="cat.id"
					@click="selectCategory(cat.id)"
				>
					{{ cat.name }}
				</view>
			</scroll-view>
		</view>
		
		<!-- 课程列表 -->
		<scroll-view 
			class="course-scroll" 
			scroll-y 
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="course-list">
				<view 
					class="course-card" 
					v-for="course in courseList" 
					:key="course.id"
					@click="goToDetail(course)"
				>
					<image class="course-cover" :src="course.cover_image || '/static/image/1.jpg'" mode="aspectFill"></image>
					<view class="course-info">
						<text class="course-title">{{ course.title }}</text>
						<view class="course-meta">
							<text class="course-difficulty">难度：{{ getDifficultyText(course.difficulty) }}</text>
							<text class="course-duration">时长：{{ course.duration }}分钟</text>
						</view>
						<view class="course-desc">{{ course.description || '暂无描述' }}</view>
						<view class="course-actions">
							<button class="add-plan-btn" @click.stop="addToPlan(course)">加入学习计划</button>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 加载更多 -->
			<view class="load-more" v-if="hasMore">
				<text class="load-more-text">加载中...</text>
			</view>
			
			<!-- 没有更多 -->
			<view class="no-more" v-if="!hasMore && courseList.length > 0">
				<text class="no-more-text">没有更多了</text>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-if="!loading && courseList.length === 0">
				<image class="ui-state-icon" src="/static/icons/book-muted.png" />
				<text class="empty-text">暂无课程</text>
			</view>
		</scroll-view>
		
		<!-- 加载中 -->
		<view class="loading-overlay" v-if="loading && courseList.length === 0">
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
				refreshing: false,
				courseList: [],
				categories: [],
				selectedCategory: null,
				searchKeyword: '',
				page: 0,
				pageSize: 10,
				hasMore: true,
				total: 0
			}
		},
		onLoad(options) {
			// 如果从技能页跳转过来，设置技能筛选
			if (options.skill) {
				this.searchKeyword = decodeURIComponent(options.skill)
			}
			this.loadCategories()
			this.loadCourses()
		},
		methods: {
			// 加载分类
			async loadCategories() {
				try {
					const res = await courseAPI.getCategories()
					if (res && Array.isArray(res)) {
						this.categories = res
					}
				} catch (error) {
					console.error('加载分类失败:', error)
				}
			},
			
			// 加载课程列表
			async loadCourses(reset = false) {
				if (this.loading && !reset) return
				
				this.loading = true
				if (reset) {
					this.page = 0
					this.courseList = []
					this.hasMore = true
				}
				
				try {
					const params = {
						skip: this.page * this.pageSize,
						limit: this.pageSize
					}
					
					if (this.selectedCategory) {
						params.category_id = this.selectedCategory
					}
					
					if (this.searchKeyword) {
						params.search = this.searchKeyword
					}
					
					const res = await courseAPI.getCourses(params)
					if (res && res.courses) {
						if (reset) {
							this.courseList = res.courses
						} else {
							this.courseList = [...this.courseList, ...res.courses]
						}
						this.total = res.total
						this.hasMore = this.courseList.length < res.total
						this.page++
					}
				} catch (error) {
					console.error('加载课程失败:', error)
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				} finally {
					this.loading = false
					this.refreshing = false
				}
			},
			
			// 选择分类
			selectCategory(categoryId) {
				this.selectedCategory = categoryId
				this.loadCourses(true)
			},
			
			// 搜索输入
			handleSearchInput() {
				// 可以添加防抖
				clearTimeout(this.searchTimer)
				this.searchTimer = setTimeout(() => {
					this.handleSearch()
				}, 500)
			},
			
			// 搜索
			handleSearch() {
				this.loadCourses(true)
			},
			
			// 下拉刷新
			onRefresh() {
				this.refreshing = true
				this.loadCourses(true)
			},
			
			// 加载更多
			loadMore() {
				if (this.hasMore && !this.loading) {
					this.loadCourses()
				}
			},
			
			// 获取难度文本
			getDifficultyText(level) {
				const levels = {
					1: '入门',
					2: '初级',
					3: '中级',
					4: '高级',
					5: '专家'
				}
				return levels[level] || '未知'
			},
			
			// 跳转到详情
			goToDetail(course) {
				uni.navigateTo({
					url: `/pages/teach/TeachDetail?courseId=${course.id}`
				})
			},
			
			// 加入学习计划
			async addToPlan(course) {
				if (!course) return
				try {
					await courseAPI.addFavorite({
						course_id: course.id,
						is_favorite: false,
						is_studying: true
					})
					uni.showToast({
						title: '已加入学习计划',
						icon: 'success',
						duration: 2000
					})
				} catch (error) {
					uni.showToast({
						title: error.message || '操作失败，请重试',
						icon: 'none',
						duration: 2000
					})
				}
			}
		}
	}
</script>

<style scoped>
	.teach-course-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		display: flex;
		flex-direction: column;
	}
	
	.search-section {
		padding: 30rpx;
		padding-bottom: 20rpx;
	}
	
	.search-box {
		display: flex;
		align-items: center;
		background: #FFFFFF;
		border-radius: 50rpx;
		padding: 0 30rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}
	
	.search-input {
		flex: 1;
		height: 80rpx;
		font-size: 28rpx;
		color: var(--color-ink);
	}
	
	.search-icon {
		font-size: 36rpx;
		margin-left: 20rpx;
	}
	
	.filter-section {
		padding: 0 30rpx 20rpx;
	}
	
	.filter-scroll {
		white-space: nowrap;
	}
	
	.filter-item {
		display: inline-block;
		padding: 16rpx 32rpx;
		margin-right: 20rpx;
		background: rgba(255, 255, 255, 0.8);
		border-radius: 30rpx;
		font-size: 26rpx;
		color: var(--color-muted);
		border: 2rpx solid var(--color-line);
		transition: transform 160ms ease, background-color 160ms ease;
	}
	
	.filter-item.active {
		background: var(--color-accent);
		color: #ffffff;
		font-weight: 700;
		border-color: var(--color-accent);
	}
	
	.course-scroll {
		flex: 1;
		height: calc(100vh - 200rpx);
	}
	
	.course-list {
		padding: 0 30rpx 30rpx;
	}
	
	.course-card {
		width: 100%;
		margin-bottom: 30rpx;
		background: var(--color-surface);
		border-radius: 28rpx;
		overflow: hidden;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		transition: transform 160ms ease, background-color 160ms ease;
	}

	.course-card:active {
		transform: scale(0.98);
		box-shadow: var(--shadow-card);
	}

	.course-cover {
		width: 100%;
		height: 400rpx;
		transition: transform 0.4s;
	}

	.course-card:active .course-cover {
		transform: scale(1.02);
	}

	.course-info {
		padding: 35rpx;
	}

	.course-title {
		font-size: 38rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 24rpx;
		letter-spacing: 0.5rpx;
	}

	.course-meta {
		display: flex;
		justify-content: space-between;
		margin-bottom: 24rpx;
	}

	.course-difficulty,
	.course-duration {
		font-size: 26rpx;
		color: var(--color-muted);
		padding: 10rpx 20rpx;
		background: var(--color-surface);
		border-radius: 12rpx;
		font-weight: 500;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.course-desc {
		font-size: 28rpx;
		color: var(--color-muted);
		line-height: 1.7;
		margin-bottom: 35rpx;
		letter-spacing: 0.3rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.course-actions {
		display: flex;
		justify-content: center;
	}

	.add-plan-btn {
		background: var(--color-accent);
		color: #ffffff;
		border: none;
		border-radius: 50rpx;
		padding: 22rpx 70rpx;
		font-size: 30rpx;
		font-weight: 700;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		letter-spacing: 0.5rpx;
	}

	.add-plan-btn::after {
		border: none;
	}

	.add-plan-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}
	
	.load-more,
	.no-more {
		text-align: center;
		padding: 40rpx;
	}
	
	.load-more-text,
	.no-more-text {
		font-size: 26rpx;
		color: var(--color-muted);
	}
	
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 200rpx 40rpx;
	}
	
	.empty-icon {
		font-size: 120rpx;
		margin-bottom: 30rpx;
		opacity: 0.6;
	}
	
	.empty-text {
		font-size: 32rpx;
		color: var(--color-muted);
	}
	
	.loading-overlay {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 200rpx 40rpx;
	}
	
	.loading-text {
		font-size: 28rpx;
		color: var(--color-muted);
	}

.filter-item.active, .add-plan-btn { color: white; } .course-card { box-shadow: none; } .course-info { min-width: 0; }


.search-icon-button { margin: 0; padding: 20rpx 0 20rpx 20rpx; background: transparent; display: flex; align-items: center; }
.search-box { border-radius: 18rpx; }
.course-cover { height: 320rpx; }
.course-info { padding: 28rpx; }
.course-title { font-size: 33rpx; margin-bottom: 16rpx; }
.course-meta { justify-content: flex-start; gap: 12rpx; flex-wrap: wrap; }
.course-difficulty, .course-duration { font-size: 23rpx; background: var(--color-bg); box-shadow: none; border: none; }
.add-plan-btn { width: 100%; border-radius: 16rpx; padding: 14rpx 24rpx; font-size: 28rpx; box-shadow: none; }
.course-scroll { height: calc(100vh - 240rpx - var(--window-top, 0px)); height: calc(100dvh - 240rpx - var(--window-top, 0px)); }

</style>

