<template>
  <view class="home-container">
    <view class="home-intro">
      <view><text class="page-kicker">LET’S PLAY VOLLEYBALL</text><text class="home-title">热爱，从这一球开始。</text><text class="page-subtitle">从第一次触球，到每一次进步。</text></view>
      <image class="intro-ball" src="/static/icons/ball-volleyball-active.png" mode="aspectFit" />
    </view>
    <view class="hero">
      <swiper class="banner-swiper" :indicator-dots="true" :autoplay="false" :duration="400" circular indicator-color="rgba(255,255,255,.4)" indicator-active-color="#ffffff">
        <swiper-item v-for="(item, index) in bannerList" :key="index"><image class="banner-image" :src="item" mode="aspectFill" @error="bannerList[index] = '/static/banners/volley-2.jpg'" /></swiper-item>
      </swiper>
      <view class="hero-footer"><view><text class="hero-title">你的主场，随时开练</text><text class="hero-desc">规则 · 技巧 · 实战，循序进阶</text></view><button role="button" tabindex="0" class="hero-action" @keydown.enter.prevent="goToLearning" @keydown.space.prevent="goToLearning" @click="goToLearning">开始练习<image class="ui-icon" src="/static/icons/arrow-up-right-white.png" /></button></view>
    </view>
    <view class="card-section">
      <button role="button" tabindex="0" class="entry-card" @keydown.enter.prevent="goToKnowledge" @keydown.space.prevent="goToKnowledge" @click="goToKnowledge"><image class="entry-icon" src="/static/icons/book-active.png" /><text class="card-title">排球知识</text><text class="card-desc">先读懂球场，再走上球场</text><image class="entry-arrow" src="/static/icons/arrow-up-right.png" /></button>
      <button role="button" tabindex="0" class="entry-card" @keydown.enter.prevent="goToQuiz" @keydown.space.prevent="goToQuiz" @click="goToQuiz"><image class="entry-icon" src="/static/icons/map-pin-active.png" /><text class="card-title">本地课程</text><text class="card-desc">找个球场，一起练起来</text><image class="entry-arrow" src="/static/icons/arrow-up-right.png" /></button>
    </view>
    <view class="recommend-section">
      <view class="section-heading"><text class="section-title">为你推荐</text><button role="button" tabindex="0" class="text-action" @keydown.enter.prevent="goToCourses" @keydown.space.prevent="goToCourses" @click="goToCourses">全部课程<image class="small-arrow" src="/static/icons/chevron-right-muted.png" /></button></view>
      <view v-if="loading" aria-label="正在加载课程"><view class="ui-skeleton" /><view class="ui-skeleton" /></view>
      <view class="ui-state" v-else-if="!recommendList.length"><image class="ui-state-icon" src="/static/icons/book-muted.png" /><text class="ui-state-title">{{ loadError ? '课程暂时没加载出来' : '下一次进步，值得期待' }}</text><text class="ui-state-desc">{{ loadError ? '请检查网络，或稍后再试。' : '课程正在准备中，先去了解排球规则吧。' }}</text><button role="button" tabindex="0" class="ui-state-action" @keydown.enter.prevent="loadError ? loadRecommendCourses() : goToKnowledge()" @keydown.space.prevent="loadError ? loadRecommendCourses() : goToKnowledge()" @click="loadError ? loadRecommendCourses() : goToKnowledge()">{{ loadError ? '重新加载' : '学习排球规则' }}</button></view>
      <view class="recommend-list" v-else>
        <button role="button" tabindex="0" class="recommend-item" v-for="item in recommendList" :key="item.id" @keydown.enter.prevent="goToDetail(item)" @keydown.space.prevent="goToDetail(item)" @click="goToDetail(item)">
          <image class="recommend-image" :src="item.image" mode="aspectFill" @error="item.image = '/static/banners/volley-2.jpg'" />
          <view class="recommend-info"><text class="course-label">精选训练<text v-if="item.duration"> · {{ item.duration }} 分钟</text></text><text class="recommend-title">{{ item.title }}</text><text class="recommend-desc">{{ item.desc }}</text></view>
          <image class="small-arrow" src="/static/icons/chevron-right-muted.png" />
        </button>
      </view>
    </view>
    <text class="home-signoff">每一次触球，都是新的开始。</text>
  </view>
</template>
<script>
	import { courseAPI, bannerAPI } from '@/utils/api.js'
	import { resolveMediaUrl } from '@/utils/config.js'
	
	export default {
		data() {
			return {
				userInfo: null,
				loading: false,
                loadError: false,
				bannerList: ['/static/banners/volley-1.jpg', '/static/banners/volley-2.jpg', '/static/banners/volley-3.jpg'],
				recommendList: []
			}
		},
		onShow() {
			// 检查登录状态
			this.checkLoginStatus()
			// 加载Banner
			this.loadBanners()
			// 加载推荐内容
			this.loadRecommendCourses()
		},
		methods: {
			checkLoginStatus() {
				const token = uni.getStorageSync('token')
				const userInfo = uni.getStorageSync('userInfo')
				
				if (!token || !userInfo) {
					// 未登录，跳转到登录页
					uni.reLaunch({
						url: '/pages/auth/Login'
					})
					return
				}
				
				this.userInfo = userInfo
			},
			
			// 从后端加载Banner
			async loadBanners() {
				try {
					const banners = await bannerAPI.getBanners()
					if (banners && banners.length > 0) {
						this.bannerList = banners.map(banner => {
							// 如果image_url是相对路径，需要拼接完整URL
							return resolveMediaUrl(banner.image_url)
						})
					} else {
						// 如果没有数据，使用默认图片
						this.bannerList = [
							'/static/banners/volley-1.jpg',
							'/static/banners/volley-2.jpg',
							'/static/banners/volley-3.jpg'
						]
					}
				} catch (error) {
					console.error('加载Banner失败:', error)
					// 加载失败时使用默认图片
					this.bannerList = [
						'/static/banners/volley-1.jpg',
						'/static/banners/volley-2.jpg',
						'/static/banners/volley-3.jpg'
					]
				}
			},
			
			// 从后端加载推荐课程
			async loadRecommendCourses() {
				this.loading = true
                this.loadError = false
				try {
					const res = await courseAPI.getCourses({ limit: 5 })
					if (res && res.courses) {
						this.recommendList = res.courses.map(course => ({
							id: course.id,
							title: course.title,
							desc: course.description || '',
							image: resolveMediaUrl(course.cover_image) || '/static/banners/volley-2.jpg',
                            duration: course.duration,
							path: '/pages/teach/TeachDetail',
							skill: course.skill_type || ''
						}))
					}
				} catch (error) {
					console.error('加载推荐课程失败:', error)
                    this.loadError = true
					this.recommendList = []
				} finally {
					this.loading = false
				}
			},
			goToKnowledge() {
				uni.navigateTo({
					url: '/pages/teach/TeachRule'
				})
			},
			goToLearning() {
                uni.switchTab({ url: '/pages/teach/TeachHome' })
            },
            goToCourses() {
                uni.navigateTo({ url: '/pages/teach/TeachCourse' })
            },
            goToQuiz() {
				uni.switchTab({
					url: '/pages/offline/Offline'
				})
			},
			goToDetail(item) {
				if (!item || !item.path) return;
				try {
					let url = item.path
					if (item.id) {
						// 如果有课程ID，传递ID
						url = `${item.path}?courseId=${item.id}`
					} else if (item.skill) {
						// 否则传递技能类型
						url = `${item.path}?skill=${encodeURIComponent(item.skill)}`
					}
					uni.navigateTo({
						url: url,
						fail: (err) => {
							console.error('导航失败:', err);
							uni.showToast({
								title: '页面跳转失败',
								icon: 'none',
								duration: 2000
							});
						}
					});
				} catch (e) {
					console.error('跳转错误:', e);
					uni.showToast({
						title: '页面跳转失败',
						icon: 'none',
						duration: 2000
					});
				}
			}
		}
	}
</script>
<style scoped>
.home-container { padding: 36rpx 36rpx 40rpx; background: var(--color-bg); }
.home-intro { display: flex; align-items: center; justify-content: space-between; margin: 10rpx 0 32rpx; gap: 16rpx; }
.home-title { display: block; font-size: 43rpx; font-weight: 750; letter-spacing: -1.5rpx; line-height: 1.35; }
.home-intro .page-subtitle { margin-top: 12rpx; }
.intro-ball { width: 66rpx; height: 66rpx; flex-shrink: 0; transform: rotate(-16deg); }
.hero { border-radius: 28rpx; overflow: hidden; background: var(--color-surface); border: 1rpx solid var(--color-line); }
.banner-swiper { height: 330rpx; width: 100%; background: #26394a; }
.banner-image { width: 100%; height: 100%; }
.hero-footer { display: flex; justify-content: space-between; align-items: center; padding: 26rpx 24rpx; gap: 12rpx; }
.hero-title { display: block; font-size: 29rpx; font-weight: 700; }
.hero-desc { display: block; font-size: 21rpx; color: var(--color-muted); margin-top: 8rpx; }
.hero-action { margin: 0; padding: 0 20rpx; min-height: 78rpx; display: flex; align-items: center; gap: 8rpx; background: var(--color-accent); color: white; font-size: 25rpx; border-radius: 16rpx; white-space: nowrap; flex-shrink: 0; }
.hero-action .ui-icon { width: 28rpx; height: 28rpx; }
.card-section { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20rpx; margin: 24rpx 0 36rpx; }
.entry-card { width: 100%; margin: 0; padding: 24rpx; text-align: left; line-height: 1.5; background: #edf0e9; border-radius: 22rpx; position: relative; }
.entry-card:nth-child(2) { background: #f5ede5; }
.entry-icon { width: 42rpx; height: 42rpx; margin-bottom: 14rpx; display: block; }
.entry-arrow { position: absolute; right: 22rpx; top: 26rpx; width: 30rpx; height: 30rpx; }
.card-title { display: block; font-size: 29rpx; font-weight: 700; color: var(--color-ink); }
.card-desc { display: block; font-size: 21rpx; color: var(--color-muted); margin-top: 8rpx; }
.section-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20rpx; }
.section-title { font-size: 34rpx; font-weight: 750; }
.text-action { background: transparent; display: flex; align-items: center; margin: 0; padding: 10rpx 0 10rpx 16rpx; font-size: 24rpx; color: var(--color-muted); }
.small-arrow { width: 28rpx; height: 28rpx; flex-shrink: 0; }
.recommend-list { display: flex; flex-direction: column; gap: 18rpx; }
.recommend-item { display: flex; align-items: center; gap: 20rpx; width: 100%; padding: 20rpx; background: white; border: 1rpx solid var(--color-line); border-radius: 22rpx; text-align: left; line-height: 1.5; }
.recommend-image { width: 160rpx; height: 160rpx; border-radius: 14rpx; flex-shrink: 0; background: #edf0e9; }
.recommend-info { flex: 1; min-width: 0; }
.course-label { display: block; color: var(--color-accent); font-size: 20rpx; margin-bottom: 8rpx; }
.recommend-title { display: block; font-size: 28rpx; font-weight: 650; line-height: 1.5; }
.recommend-desc { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; color: var(--color-muted); font-size: 23rpx; line-height: 1.6; margin-top: 8rpx; }
.home-signoff { display: block; text-align: center; margin: 36rpx 0 0; color: var(--color-muted); font-size: 21rpx; letter-spacing: 2rpx; }
.hero-action:active, .entry-card:active, .recommend-item:active { transform: scale(.985); }
@media (min-width: 768px) { .home-container { padding: 40px; } .banner-swiper { height: 340px; } .recommend-list { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); } }
</style>
