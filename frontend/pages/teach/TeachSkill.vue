<template>
	<view class="teach-skill-container">
        <view class="page-heading"><text class="page-title">专注一项，突破一点。</text><text class="page-subtitle">从垫球到扣球，找到你想提升的技术。</text></view>
		<view class="ui-state" v-if="!loading && !skillList.length"><image class="ui-state-icon" src="/static/icons/ball-volleyball-muted.png" /><text class="ui-state-title">{{ loadError ? '技能内容暂时没加载出来' : '技能课程正在准备中' }}</text><text class="ui-state-desc">{{ loadError ? '请检查网络连接后重试。' : '稍后回来，开启你的专项练习。' }}</text><button v-if="loadError" class="ui-state-action" @click="loadSkillTypes">重新加载</button></view>
        <view class="skill-grid">
			<view 
				class="skill-card" 
				v-for="(skill, index) in skillList" 
				:key="index"
				@click="goToDetail(skill)"
			>
				<image class="skill-icon" src="/static/icons/ball-volleyball-active.png" />
				<text class="skill-title">{{ skill.title }}</text>
				<text class="skill-desc">{{ skill.desc }}</text>
				<view class="skill-meta">
					<text class="course-count" v-if="skillCourses[skill.skillType]">
						{{ skillCourses[skill.skillType] }}个课程
					</text>
				</view>
				<view class="skill-detail-btn">
					<text>查看详情</text>
				</view>
			</view>
			
			<!-- 加载中 -->
			<view class="loading-container" v-if="loading">
				<text class="loading-text">加载中...</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { courseAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loading: false,
                loadError: false,
				skillList: [],
				skillCourses: {} // 存储每个技能对应的课程数量
			}
		},
		onLoad() {
			this.loadSkillTypes()
		},
		methods: {
			// 从后端加载技能类型列表
			async loadSkillTypes() {
				this.loading = true
                this.loadError = false
				try {
					const skills = await courseAPI.getSkillTypes()
					if (skills && Array.isArray(skills)) {
						this.skillList = skills.map(skill => ({
							icon: skill.icon || '🏐',
							title: skill.name,
							skillType: skill.skillType,
							desc: skill.description || ''
						}))
						// 加载每个技能的课程数量
						await this.loadSkillCourses()
					}
				} catch (error) {
					console.error('加载技能类型失败:', error)
                    this.loadError = true
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			
			// 加载每个技能的课程数量
			async loadSkillCourses() {
				try {
					for (const skill of this.skillList) {
						try {
							const res = await courseAPI.getCourses({
								skill_type: skill.skillType,
								limit: 1
							})
							if (res) {
								this.skillCourses[skill.skillType] = res.total || 0
							}
						} catch (error) {
							console.error(`加载${skill.title}课程失败:`, error)
						}
					}
				} catch (error) {
					console.error('加载技能课程失败:', error)
				}
			},
			
			goToDetail(skill) {
				if (!skill || !skill.title) return
				try {
					// 优先跳转到课程列表页，显示该技能的课程
					uni.navigateTo({
						url: `/pages/teach/TeachCourse?skill=${encodeURIComponent(skill.skillType)}`,
						fail: () => {
							// 如果失败，跳转到详情页
							uni.navigateTo({
								url: `/pages/teach/TeachDetail?skill=${encodeURIComponent(skill.title)}`
							})
						}
					})
				} catch (e) {
					console.error('跳转错误:', e)
					uni.showToast({
						title: '页面跳转失败',
						icon: 'none',
						duration: 2000
					})
				}
			}
		}
	}
</script>

<style scoped>
	.teach-skill-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
	}

	.skill-grid {
		display: flex;
		flex-direction: column;
		gap: 30rpx;
	}

	.skill-card {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 45rpx 40rpx;
		box-shadow: var(--shadow-card);
		display: flex;
		flex-direction: column;
		align-items: center;
		transition: transform 160ms ease, background-color 160ms ease;
		border: 1rpx solid var(--color-line);
		position: relative;
		overflow: hidden;
	}

	.skill-card::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, var(--color-line) 0%, transparent 70%);
		opacity: 0;
		transition: opacity 0.4s;
	}

	.skill-card:active::before {
		opacity: 1;
	}

	.skill-card:active {
		transform: translateY(-6rpx) scale(0.98);
		box-shadow: var(--shadow-card);
	}

	.skill-icon {
		font-size: 110rpx;
		margin-bottom: 24rpx;
		filter: drop-shadow(0 6rpx 12rpx rgba(0, 0, 0, 0.15));
		transition: transform 0.3s;
	}

	.skill-card:active .skill-icon {
		transform: scale(1.15) rotate(5deg);
	}

	.skill-title {
		font-size: 38rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 18rpx;
		letter-spacing: 0.5rpx;
	}

	.skill-desc {
		font-size: 28rpx;
		color: var(--color-muted);
		text-align: center;
		margin-bottom: 20rpx;
		line-height: 1.6;
		opacity: 0.85;
	}
	
	.skill-meta {
		margin-bottom: 20rpx;
	}
	
	.course-count {
		font-size: 24rpx;
		color: var(--color-accent);
		font-weight: 600;
		padding: 8rpx 20rpx;
		background: rgba(255, 107, 107, 0.1);
		border-radius: 20rpx;
	}
	
	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 100rpx;
	}
	
	.loading-text {
		font-size: 28rpx;
		color: var(--color-muted);
	}

	.skill-detail-btn {
		margin-top: 10rpx;
		padding: 18rpx 50rpx;
		background: var(--color-accent);
		border-radius: 50rpx;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
	}

	.skill-card:active .skill-detail-btn {
		box-shadow: var(--shadow-card);
		transform: scale(1.05);
	}

	.skill-detail-btn text {
		font-size: 28rpx;
		color: var(--color-ink);
		font-weight: 700;
		letter-spacing: 0.5rpx;
	}

.skill-detail-btn text { color: white; } .skill-card { box-shadow: none; align-items: flex-start; } .skill-title { font-size: 34rpx; }

.skill-icon { width: 64rpx; height: 64rpx; filter: none; margin-bottom: 24rpx; } .skill-card { padding: 28rpx; } .skill-desc { line-height: 1.7; } .skill-detail-btn { padding: 18rpx 24rpx; border-radius: 14rpx; }
</style>

