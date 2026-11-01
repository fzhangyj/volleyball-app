<template>
	<view class="teach-react-container">
		<view class="page-header">
			<view class="page-title">反应力训练营</view>
			<view class="page-subtitle">三种小游戏，从不同维度唤醒神经反射</view>
		</view>

		<view class="mode-tabs">
			<view 
				class="mode-tab" 
				v-for="mode in gameModes" 
				:key="mode.id"
				:class="{ active: currentMode === mode.id }"
				@click="switchMode(mode.id)"
			>
				<view class="mode-title">{{ mode.title }}</view>
				<view class="mode-desc">{{ mode.desc }}</view>
			</view>
		</view>

		<view class="score-info">
			<text class="score-text">总得分：{{ score }}</text>
			<text class="time-text">最近反应：{{ reactionTime }}ms</text>
			<text class="time-text">平均反应：{{ avgReactionTime }}ms</text>
			<button class="control-btn" @click="restartGame">重新开始</button>
		</view>

		<view class="mode-tip">
			<text>{{ currentModeInfo.tip }}</text>
		</view>

		<view class="game-area" v-if="!gameEnd">
			<view class="game-title">{{ currentModeInfo.title }}</view>

			<view class="ball-container" v-if="currentMode === 'ball'">
				<view 
					class="ball" 
					v-for="(ball, index) in ballPositions" 
					:key="index"
					:style="{ left: ball.x + 'rpx', top: ball.y + 'rpx', display: ball.visible ? 'block' : 'none' }"
					@click="hitBall(index)"
				></view>
			</view>
			<view class="game-tips" v-if="currentMode === 'ball'">锁定瞬间闪现的球体，越快点击得分越高！</view>

			<view class="color-game" v-else-if="currentMode === 'color'">
				<view class="color-card" v-if="colorPrompt" :style="{ backgroundColor: colorPrompt.displayColor }">
					<text class="color-word">{{ colorPrompt.word }}</text>
				</view>
				<view class="color-actions">
					<button class="judge-btn positive" @click="respondColor(true)">颜色一致</button>
					<button class="judge-btn negative" @click="respondColor(false)">颜色不一致</button>
				</view>
				<view class="game-tips">文字含义与背景色一致就点“颜色一致”，否则点“颜色不一致”。</view>
			</view>

			<view class="direction-game" v-else-if="currentMode === 'direction'">
				<view class="direction-card" v-if="directionPrompt">
					<text class="direction-icon">{{ directionPrompt.icon }}</text>
					<text class="direction-text">{{ directionPrompt.text }}</text>
				</view>
				<view class="direction-buttons">
					<button 
						class="direction-btn"
						v-for="btn in directionButtons"
						:key="btn.id"
						@click="answerDirection(btn.id)"
					>{{ btn.label }}</button>
				</view>
				<view class="game-tips">一句话：相信“图标”而不是“文字”，快速点对方向！</view>
			</view>
		</view>

		<view class="result-area" v-else>
			<view class="result-title">训练结束</view>
			<view class="result-stats">
				<text class="stat-item">总得分：{{ score }}</text>
				<text class="stat-item">平均反应时间：{{ avgReactionTime }}ms</text>
				<text class="stat-item">命中率：{{ hitRate }}%</text>
			</view>
			<view class="result-actions">
				<button class="retry-btn" @click="restartGame">再试一次</button>
				<button class="back-btn" @click="goBack">返回教学</button>
			</view>
		</view>
	</view>
</template>

<script>
import { navigateBack } from '@/utils/navigation.js'
	import { trainingAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				score: 0,
				reactionTime: 0,
				gameEnd: false,
				ballPositions: [],
				reactionTimes: [],
				hitCount: 0,
				totalBalls: 0,
				startTime: 0,
				gameStartTime: 0,
				gameDuration: 30000,
				intervalIds: [],
				timeoutIds: [],
				colorRoundTimer: null,
				directionRoundTimer: null,
				gameDurationTimer: null,
				gameModes: [
					{ id: 'ball', title: '灵敏点球', desc: '盯紧随机亮起的小球', tip: '视线不停扫描 3×3 区域，抢在 2 秒内点击出现的球体。' },
					{ id: 'color', title: '颜色迷惑', desc: '文字与颜色的博弈', tip: '忽略文字内容，只关注颜色是否相同，练习抑制错误反应。' },
					{ id: 'direction', title: '方向速判', desc: '图标与文字反向', tip: '相信箭头而非文字，锻炼手眼协调与专注切换。' }
				],
				currentMode: 'ball',
				colorPrompt: null,
				pendingColor: false,
				directionPrompt: null,
				directionButtons: [
					{ id: 'up', label: '↑ 上' },
					{ id: 'left', label: '← 左' },
					{ id: 'down', label: '↓ 下' },
					{ id: 'right', label: '→ 右' }
				]
			}
		},
		computed: {
			avgReactionTime() {
				if (this.reactionTimes.length === 0) return 0;
				const sum = this.reactionTimes.reduce((a, b) => a + b, 0);
				return Math.round(sum / this.reactionTimes.length);
			},
			hitRate() {
				if (this.totalBalls === 0) return 0;
				return Math.round((this.hitCount / this.totalBalls) * 100);
			},
			currentModeInfo() {
				return this.gameModes.find(mode => mode.id === this.currentMode) || this.gameModes[0];
			}
		},
		onLoad() {
			this.startGame();
		},
		onUnload() {
			this.clearTimers();
		},
		onHide() {
			// 页面隐藏时清理定时器，避免后台运行
			this.clearTimers();
		},
		methods: {
			switchMode(modeId) {
				if (this.currentMode === modeId || this.gameEnd) return;
				this.currentMode = modeId;
				this.restartGame();
			},
			startGame() {
				this.resetState();
				this.gameStartTime = Date.now(); // 记录游戏开始时间
				if (this.currentMode === 'ball') {
					this.setupBallGame();
				} else if (this.currentMode === 'color') {
					this.setupColorGame();
				} else {
					this.setupDirectionGame();
				}
				this.gameDurationTimer = setTimeout(() => {
					this.endGame();
				}, this.gameDuration);
				this.timeoutIds.push(this.gameDurationTimer);
			},
			resetState() {
				this.clearTimers();
				this.score = 0;
				this.reactionTime = 0;
				this.gameEnd = false;
				this.ballPositions = [];
				this.reactionTimes = [];
				this.hitCount = 0;
				this.totalBalls = 0;
				this.gameStartTime = 0;
				this.colorPrompt = null;
				this.colorRoundTimer = null;
				this.directionPrompt = null;
				this.directionRoundTimer = null;
				this.gameDurationTimer = null;
				this.pendingColor = false;
			},
			clearTimers() {
				this.intervalIds.forEach(id => clearInterval(id));
				this.timeoutIds.forEach(id => clearTimeout(id));
				this.intervalIds = [];
				this.timeoutIds = [];
				if (this.colorRoundTimer) {
					clearTimeout(this.colorRoundTimer);
					this.colorRoundTimer = null;
				}
				if (this.directionRoundTimer) {
					clearTimeout(this.directionRoundTimer);
					this.directionRoundTimer = null;
				}
				if (this.gameDurationTimer) {
					clearTimeout(this.gameDurationTimer);
					this.gameDurationTimer = null;
				}
			},
			setupBallGame() {
				for (let i = 0; i < 9; i++) {
					this.ballPositions.push({
						// Center the 120rpx target inside each 200rpx grid cell.
						x: (i % 3) * 200 + 40,
						y: Math.floor(i / 3) * 200 + 40,
						visible: false
					});
				}
				this.showRandomBall();
				const intervalId = setInterval(() => {
					this.showRandomBall();
				}, 1500);
				this.intervalIds.push(intervalId);
			},
			showRandomBall() {
				if (this.gameEnd || this.ballPositions.length === 0) return;
				this.ballPositions.forEach(ball => {
					ball.visible = false;
				});
				const randomIndex = Math.floor(Math.random() * this.ballPositions.length);
				if (!this.ballPositions[randomIndex] || this.gameEnd) return;
				this.ballPositions[randomIndex].visible = true;
				this.startTime = Date.now();
				this.totalBalls++;
				const hideTimer = setTimeout(() => {
					if (this.ballPositions[randomIndex] && !this.gameEnd) {
						this.ballPositions[randomIndex].visible = false;
					}
				}, 2000);
				this.timeoutIds.push(hideTimer);
			},
			setupColorGame() {
				this.nextColorPrompt();
			},
			nextColorPrompt() {
				if (this.gameEnd) return;
				const colorPool = [
					{ label: '红', value: '#FF4D4F' },
					{ label: '蓝', value: '#1677FF' },
					{ label: '绿', value: '#3CB371' },
					{ label: '黄', value: '#F9A825' }
				];
				const wordIndex = Math.floor(Math.random() * colorPool.length);
				let colorIndex = Math.floor(Math.random() * colorPool.length);
				const shouldMatch = Math.random() > 0.5;
				if (shouldMatch) {
					colorIndex = wordIndex;
				} else {
					while (colorIndex === wordIndex) {
						colorIndex = Math.floor(Math.random() * colorPool.length);
					}
				}
				this.colorPrompt = {
					word: colorPool[wordIndex].label,
					displayColor: colorPool[colorIndex].value,
					match: shouldMatch
				};
				this.startTime = Date.now();
				this.pendingColor = true;
				this.totalBalls++;
				const roundTimer = setTimeout(() => {
					this.colorRoundTimer = null;
					if (this.pendingColor) {
						this.pendingColor = false;
					}
					if (!this.gameEnd) {
						this.nextColorPrompt();
					}
				}, 2200);
				this.colorRoundTimer = roundTimer;
				this.timeoutIds.push(roundTimer);
			},
			respondColor(isMatch) {
				if (this.gameEnd || !this.pendingColor || !this.colorPrompt) return;
				this.pendingColor = false;
				if (this.colorRoundTimer) {
					clearTimeout(this.colorRoundTimer);
					this.colorRoundTimer = null;
				}
				const correct = (isMatch && this.colorPrompt.match) || (!isMatch && !this.colorPrompt.match);
				const reactionTime = Date.now() - this.startTime;
				this.handleResult(correct, reactionTime, 90);
				this.nextColorPrompt();
			},
			setupDirectionGame() {
				this.nextDirectionPrompt();
			},
			nextDirectionPrompt() {
				if (this.gameEnd) return;
				const prompts = [
					{ icon: '↑', text: '向下', answer: 'up' },
					{ icon: '↓', text: '向上', answer: 'down' },
					{ icon: '←', text: '向右', answer: 'left' },
					{ icon: '→', text: '向左', answer: 'right' }
				];
				this.directionPrompt = prompts[Math.floor(Math.random() * prompts.length)];
				this.startTime = Date.now();
				this.totalBalls++;
				const roundTimer = setTimeout(() => {
					this.directionRoundTimer = null;
					if (!this.gameEnd) {
						this.nextDirectionPrompt();
					}
				}, 2200);
				this.directionRoundTimer = roundTimer;
				this.timeoutIds.push(roundTimer);
			},
			answerDirection(directionId) {
				if (this.gameEnd || !this.directionPrompt) return;
				const correct = directionId === this.directionPrompt.answer;
				const reactionTime = Date.now() - this.startTime;
				if (this.directionRoundTimer) {
					clearTimeout(this.directionRoundTimer);
					this.directionRoundTimer = null;
				}
				this.handleResult(correct, reactionTime, 95);
				this.nextDirectionPrompt();
			},
			handleResult(success, reactionTime, baseScore = 100) {
				if (success) {
					this.reactionTime = reactionTime;
					this.reactionTimes.push(reactionTime);
					this.hitCount++;
					const bonus = Math.max(Math.round(baseScore - reactionTime / 15), 5);
					this.score += bonus;
					uni.showToast({
						title: `+${bonus}分`,
						icon: 'none',
						duration: 500
					});
				} else {
					uni.showToast({
						title: '判断失误，继续加油！',
						icon: 'none',
						duration: 500
					});
				}
			},
			hitBall(index) {
				if (!this.ballPositions[index] || !this.ballPositions[index].visible || this.gameEnd) return;
				this.ballPositions[index].visible = false;
				const reactionTime = Date.now() - this.startTime;
				this.handleResult(true, reactionTime, 110);
			},
			async endGame() {
				this.clearTimers();
				this.gameEnd = true;
				
				// 保存训练记录到后端
				try {
					const token = uni.getStorageSync('token')
					if (token) {
						await this.saveTrainingRecord()
					}
				} catch (error) {
					console.error('保存训练记录失败:', error)
				}
			},
			
			async saveTrainingRecord() {
				try {
					// 计算实际游戏时长（秒）
					const actualDuration = this.gameStartTime > 0 
						? Math.floor((Date.now() - this.gameStartTime) / 1000)
						: Math.floor(this.gameDuration / 1000)
					
					await trainingAPI.saveReactionRecord({
						game_mode: this.currentMode,
						score: this.score,
						avg_reaction_time: this.avgReactionTime,
						hit_rate: this.hitRate,
						total_rounds: this.totalBalls,
						hit_count: this.hitCount,
						duration: actualDuration
					})
				} catch (error) {
					console.error('保存训练记录失败:', error)
				}
			},
			restartGame() {
				this.startGame();
			},
			goBack() {
				navigateBack('/pages/teach/TeachHome');
			}
		}
	}
</script>

<style scoped>
	.teach-react-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
	}

	.page-header {
		margin-bottom: 35rpx;
		padding: 30rpx;
		background: var(--color-surface);
		border-radius: 24rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.page-title {
		font-size: 46rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 12rpx;
		letter-spacing: 1rpx;
	}

	.page-subtitle {
		font-size: 28rpx;
		color: var(--color-muted);
		opacity: 0.85;
		line-height: 1.5;
	}

	.mode-tabs {
		display: flex;
		gap: 20rpx;
		margin-bottom: 35rpx;
		overflow-x: auto;
	}

	.mode-tab {
		flex: 1;
		min-width: 200rpx;
		padding: 28rpx 24rpx;
		border-radius: 24rpx;
		background: var(--color-surface);
		box-shadow: var(--shadow-card);
		border: 2rpx solid transparent;
		transition: transform 160ms ease, background-color 160ms ease;
	}

	.mode-tab.active {
		border-color: #FFB347;
		background: linear-gradient(135deg, #FFF3E0 0%, #FFE8B8 100%);
		box-shadow: var(--shadow-card);
		transform: translateY(-2rpx);
	}

	.mode-title {
		font-size: 32rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 10rpx;
		letter-spacing: 0.5rpx;
	}

	.mode-desc {
		font-size: 24rpx;
		color: var(--color-muted);
		opacity: 0.85;
		line-height: 1.4;
	}

	.score-info {
		display: flex;
		flex-wrap: wrap;
		gap: 18rpx;
		align-items: center;
		justify-content: space-between;
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 28rpx;
		box-shadow: var(--shadow-card);
		margin-bottom: 24rpx;
		border: 1rpx solid var(--color-line);
	}

	.game-title {
		font-size: 42rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 35rpx;
		letter-spacing: 0.5rpx;
	}

	.score-text,
	.time-text {
		font-size: 28rpx;
		color: var(--color-muted);
		padding: 16rpx 32rpx;
		background: var(--color-surface);
		border-radius: 50rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		font-weight: 600;
		letter-spacing: 0.3rpx;
	}

	.control-btn {
		padding: 18rpx 32rpx;
		border-radius: 50rpx;
		border: none;
		background: linear-gradient(135deg, #FFD54F, #FFB347);
		color: var(--color-ink);
		font-size: 28rpx;
		font-weight: 700;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		letter-spacing: 0.5rpx;
	}

	.control-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

	.mode-tip {
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 24rpx;
		font-size: 28rpx;
		color: var(--color-muted);
		margin-bottom: 24rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		line-height: 1.7;
		letter-spacing: 0.3rpx;
	}

	.game-area {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.ball-container {
		position: relative;
		width: 600rpx;
		height: 600rpx;
		margin: 40rpx 0;
		background: var(--color-surface);
		background-image: 
			linear-gradient(var(--color-line) 1rpx, transparent 1rpx),
			linear-gradient(90deg, var(--color-line) 1rpx, transparent 1rpx);
		background-size: 200rpx 200rpx;
		border-radius: 40rpx;
		box-shadow: var(--shadow-card);
		border: 2rpx solid var(--color-line);
		position: relative;
		overflow: hidden;
	}

	.ball-container::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, var(--color-line) 0%, transparent 70%);
		animation: rotate 20s linear infinite;
	}

	@keyframes rotate {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.ball {
		position: absolute;
		width: 120rpx;
		height: 120rpx;
		background: radial-gradient(circle, var(--color-accent) 0%, #FF4757 100%);
		border-radius: 50%;
		box-shadow: var(--shadow-card);
		animation: popIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
		border: 3rpx solid rgba(255, 255, 255, 0.4);
		transition: transform 160ms ease, background-color 160ms ease;
		cursor: pointer;
		z-index: 10;
	}

	.ball::after {
		content: '';
		position: absolute;
		top: 20%;
		left: 25%;
		width: 30%;
		height: 30%;
		background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
		border-radius: 50%;
	}

	.ball:active {
		transform: scale(0.85);
		box-shadow: var(--shadow-card);
	}

	@keyframes popIn {
		0% {
			transform: scale(0) rotate(0deg);
			opacity: 0;
		}
		50% {
			transform: scale(1.25) rotate(180deg);
		}
		100% {
			transform: scale(1) rotate(360deg);
			opacity: 1;
		}
	}

	.game-tips {
		font-size: 26rpx;
		color: var(--color-muted);
		margin-top: 45rpx;
		opacity: 0.8;
		line-height: 1.6;
		text-align: center;
	}

	.color-game,
	.direction-game {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 30rpx;
		margin-top: 30rpx;
	}

	.color-card {
		width: 100%;
		height: 280rpx;
		border-radius: 32rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: var(--shadow-card);
		transition: transform 0.3s;
	}

	.color-card:active {
		transform: scale(0.98);
	}

	.color-word {
		font-size: 72rpx;
		font-weight: 700;
		color: #FFFFFF;
		text-shadow: none;
		letter-spacing: 2rpx;
	}

	.color-actions {
		display: flex;
		width: 100%;
		gap: 24rpx;
	}

	.judge-btn {
		flex: 1;
		padding: 32rpx;
		border-radius: 28rpx;
		font-size: 32rpx;
		font-weight: 700;
		border: none;
		color: #FFFFFF;
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		letter-spacing: 0.5rpx;
	}

	.judge-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

	.judge-btn.positive {
		background: linear-gradient(135deg, #66BB6A, #43A047);
	}

	.judge-btn.negative {
		background: linear-gradient(135deg, #EF5350, #D32F2F);
	}

	.direction-card {
		width: 100%;
		padding: 70rpx 20rpx;
		background: linear-gradient(135deg, #90CAF9, #42A5F5);
		border-radius: 32rpx;
		box-shadow: var(--shadow-card);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20rpx;
		color: #FFFFFF;
		border: 2rpx solid rgba(255, 255, 255, 0.2);
		transition: transform 0.3s;
	}

	.direction-card:active {
		transform: scale(0.98);
	}

	.direction-icon {
		font-size: 130rpx;
		font-weight: 700;
		filter: drop-shadow(0 6rpx 12rpx rgba(0, 0, 0, 0.2));
	}

	.direction-text {
		font-size: 36rpx;
		letter-spacing: 8rpx;
		font-weight: 600;
		text-shadow: none;
	}

	.direction-buttons {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 24rpx;
		width: 100%;
	}

	.direction-btn {
		padding: 32rpx 0;
		border-radius: 28rpx;
		background: var(--color-surface);
		font-size: 34rpx;
		font-weight: 700;
		color: var(--color-ink);
		border: 2rpx solid var(--color-line);
		box-shadow: var(--shadow-card);
		transition: transform 160ms ease, background-color 160ms ease;
		letter-spacing: 0.5rpx;
	}

	.direction-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
		background: linear-gradient(135deg, #FFFBF0 0%, #FFFFFF 100%);
	}

	.result-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 70rpx 45rpx;
		background: var(--color-surface);
		border-radius: 28rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}

	.result-title {
		font-size: 44rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 45rpx;
		letter-spacing: 1rpx;
		position: relative;
		padding-bottom: 20rpx;
	}

	.result-title::after {
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

	.result-stats {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
		width: 100%;
		margin-bottom: 45rpx;
	}

	.stat-item {
		font-size: 32rpx;
		color: var(--color-muted);
		padding: 24rpx;
		background: var(--color-surface);
		border-radius: 16rpx;
		text-align: center;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		font-weight: 600;
		letter-spacing: 0.3rpx;
	}

	.result-actions {
		display: flex;
		gap: 24rpx;
		width: 100%;
	}

	.retry-btn,
	.back-btn {
		flex: 1;
		padding: 28rpx;
		border-radius: 50rpx;
		font-size: 30rpx;
		font-weight: 700;
		border: none;
		transition: transform 160ms ease, background-color 160ms ease;
		letter-spacing: 0.5rpx;
	}

	.retry-btn {
		background: var(--color-accent);
		color: #ffffff;
		box-shadow: var(--shadow-card);
		border: 2rpx solid rgba(255, 255, 255, 0.3);
	}

	.retry-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

	.back-btn {
		background: linear-gradient(135deg, rgba(245, 245, 245, 0.9) 0%, rgba(238, 238, 238, 0.9) 100%);
		color: var(--color-muted);
		box-shadow: var(--shadow-card);
		border: 2rpx solid rgba(0, 0, 0, 0.05);
	}

	.back-btn:active {
		transform: translateY(-2rpx) scale(0.97);
		box-shadow: var(--shadow-card);
	}

.start-btn, .retry-btn { color: white; background: var(--color-accent); box-shadow: none; } .mode-card.active { border-color: var(--color-accent); background: var(--color-accent-soft); }


.page-header { padding: 20rpx 0 30rpx; background: transparent; border: none; box-shadow: none; }
.page-title { font-size: 44rpx; }
.mode-tabs { gap: 12rpx; }
.mode-tab { padding: 22rpx 12rpx; border-radius: 18rpx; box-shadow: none; }
.mode-tab.active { border-color: var(--color-accent); background: var(--color-accent-soft); }
.control-btn { background: var(--color-accent); color: white; box-shadow: none; }
.score-info, .game-area, .result-area { box-shadow: none; border: 1rpx solid var(--color-line); }
.game-area { background: white; border-radius: 24rpx; padding: 24rpx 12rpx; }
.ball-container { border-radius: 24rpx; box-shadow: none; }
.ball-container::before, .ball::after { display: none; }
.ball { background: var(--color-accent); box-shadow: none; }

</style>

