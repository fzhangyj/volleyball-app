<template>
	<view class="teach-rule-container">
		<view class="content-section" v-if="!loading && ruleContents.length > 0">
			<template v-for="(rule, index) in ruleContents" :key="rule.id">
				<view v-if="index === 0" class="rule-title">{{ rule.title }}</view>
				
				<view v-if="index === 0" class="basic-info">
					<text class="rule-text">{{ rule.content }}</text>
				</view>
				
				<view v-else class="rule-item">
					<text class="rule-subtitle">{{ rule.section_title || rule.title }}</text>
					<image v-if="rule.image_url" class="rule-image" :src="rule.image_url" mode="widthFix"></image>
					<text class="rule-text" v-for="(line, lineIndex) in rule.content.split('\n')" :key="lineIndex">{{ line }}</text>
				</view>
			</template>
		</view>
		
		<view v-if="loading" class="loading-container">
			<text>加载中...</text>
		</view>

		<view class="ui-state" v-if="!loading && !ruleContents.length"><image class="ui-state-icon" src="/static/icons/book-muted.png" /><text class="ui-state-title">{{ loadError ? '规则内容暂时没加载出来' : '规则内容正在准备中' }}</text><text class="ui-state-desc">{{ loadError ? '请检查网络连接后重试。' : '稍后回来，一起读懂球场。' }}</text><button v-if="loadError" class="ui-state-action" @click="loadRuleContent">重新加载</button></view>
        <view class="learn-button" v-if="!loading && ruleContents.length" @click="saveProgress">
			<text class="button-text">我学会了！</text>
		</view>
	</view>
</template>

<script>
	import { ruleAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				ruleContents: [],
				loading: false,
                loadError: false
			}
		},
		onLoad() {
			this.loadRuleContent()
		},
		methods: {
			async loadRuleContent() {
				this.loading = true
                this.loadError = false
				try {
					const res = await ruleAPI.getRuleContent()
					if (res && res.sections) {
						this.ruleContents = res.sections
					}
				} catch (error) {
					console.error('加载规则内容失败:', error)
                    this.loadError = true
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			async saveProgress() {
				try {
					const token = uni.getStorageSync('token')
					if (!token) {
						uni.showToast({
							title: '请先登录',
							icon: 'none'
						})
						return
					}
					
					await ruleAPI.saveRuleProgress({})
					
					uni.showToast({
						title: '进度已保存',
						icon: 'success',
						duration: 2000
					});
				} catch (error) {
					console.error('保存进度失败:', error)
					uni.showToast({
						title: '保存失败，请重试',
						icon: 'none'
					})
				}
			}
		}
	}
</script>

<style scoped>
	.teach-rule-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
		padding-bottom: 150rpx;
	}

	.content-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 45rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.rule-title {
		font-size: 44rpx;
		font-weight: 700;
		color: var(--color-ink);
		text-align: center;
		margin-bottom: 45rpx;
		letter-spacing: 1rpx;
		position: relative;
		padding-bottom: 20rpx;
	}

	.rule-title::after {
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

	.rule-item {
		margin-bottom: 45rpx;
	}

	.basic-info {
		margin-bottom: 45rpx;
		padding: 35rpx;
		background: linear-gradient(135deg, #FFF8E1 0%, #FFE8B8 100%);
		border-radius: 24rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.rule-subtitle {
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		display: block;
		margin-bottom: 24rpx;
		letter-spacing: 0.5rpx;
		position: relative;
		padding-left: 20rpx;
	}

	.rule-subtitle::before {
		content: '';
		position: absolute;
		left: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 6rpx;
		height: 28rpx;
		background: var(--color-accent);
		border-radius: 3rpx;
	}

	.rule-image {
		width: 100%;
		border-radius: 16rpx;
		margin: 24rpx 0;
		box-shadow: var(--shadow-card);
	}

	.rule-text {
		font-size: 28rpx;
		color: var(--color-muted);
		line-height: 1.9;
		display: block;
		margin-bottom: 18rpx;
		letter-spacing: 0.3rpx;
	}

	.learn-button {
		position: fixed;
		bottom: 120rpx;
		left: 50%;
		transform: translateX(-50%);
		width: 80%;
		background: var(--color-accent);
		border-radius: 50rpx;
		padding: 32rpx;
		text-align: center;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
	}

	.learn-button:active {
		transform: translateX(-50%) translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

	.button-text {
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		letter-spacing: 1rpx;
	}

.button-text { color: white; } .content-section { box-shadow: none; } .rule-text { line-height: 1.9; }

</style>

