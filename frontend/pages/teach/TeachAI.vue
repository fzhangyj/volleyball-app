<template>
	<view class="ai-coach-container">
		<!-- 顶部标题栏 -->
		<view class="header">
			<button class="back-btn" role="button" tabindex="0" aria-label="返回教学" @click="goBack" @keydown.enter.prevent="goBack" @keydown.space.prevent="goBack">
				<image class="ui-icon" src="/static/icons/arrow-left.png" />
			</button>
			<text class="title">AI教练</text>
			<button class="history-btn" role="button" tabindex="0" aria-label="查看历史会话" @click="showHistory = true" @keydown.enter.prevent="showHistory = true" @keydown.space.prevent="showHistory = true">
				<image class="ui-icon" src="/static/icons/history.png" />
			</button>
		</view>
		
		<!-- 聊天区域 -->
		<scroll-view 
			class="chat-area" 
			scroll-y 
			:scroll-top="scrollTop"
			scroll-with-animation
			@scrolltoupper="loadMoreHistory"
		>
			<!-- 欢迎语 -->
			<view class="welcome-section" v-if="messages.length === 0">
				<image class="ai-avatar" src="/static/icons/sparkles-active.png" />
				<text class="welcome-title">你好，我是AI排球教练</text>
				<text class="welcome-desc">我可以帮你解答排球技术、规则、训练等问题</text>
				
				<!-- 预设问题 -->
				<view class="preset-section">
					<text class="preset-title">你可以这样问我：</text>
					<view class="preset-list">
						<view 
							class="preset-item"
							v-for="q in presetQuestions"
							:key="q.id"
							@click="askPresetQuestion(q.question)"
						>
							<image class="preset-icon" src="/static/icons/arrow-up-right-muted.png" />
							<text class="preset-text">{{ q.question }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 消息列表 -->
			<view class="messages-container" v-if="messages.length > 0">
				<view 
					class="message-item"
					:class="{ 'user-message': msg.role === 'user', 'ai-message': msg.role === 'assistant' }"
					v-for="(msg, index) in messages"
					:key="index"
				>
					<view class="message-avatar">
						<image class="ui-icon" :src="msg.role === 'user' ? '/static/icons/user.png' : '/static/icons/sparkles-active.png'" />
					</view>
					<view class="message-content">
						<view class="message-bubble">
							<text class="message-text" selectable>{{ msg.content }}</text>
						</view>
						<text class="message-time" v-if="msg.time">{{ msg.time }}</text>
					</view>
				</view>
				
				<!-- AI正在输入 -->
				<view class="message-item ai-message" v-if="isLoading">
					<view class="message-avatar">
						<image class="ui-icon" src="/static/icons/sparkles-active.png" />
					</view>
					<view class="message-content">
						<view class="message-bubble typing">
							<view class="typing-dots">
								<view class="dot"></view>
								<view class="dot"></view>
								<view class="dot"></view>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<!-- 底部输入区域 -->
		<view class="input-area">
			<view class="input-wrapper">
				<textarea
					class="input-field"
					v-model="inputText"
					placeholder="输入你的问题..."
					placeholder-style="color: #737b75"
					:maxlength="500"
					:auto-height="true"
					:show-confirm-bar="false"
					@confirm="sendMessage"
				/>
			</view>
			<button
				class="send-btn"
				role="button"
				tabindex="0"
				:class="{ 'disabled': !canSend }"
				:disabled="!canSend"
				:aria-disabled="!canSend"
				aria-label="发送消息"
				@click="sendMessage"
				@keydown.enter.prevent="sendMessage"
				@keydown.space.prevent="sendMessage"
			>
				<image class="send-icon" :src="isLoading ? '/static/icons/clock-muted.png' : '/static/icons/send-white.png'" />
			</button>
		</view>
		
		<!-- 历史会话弹窗 -->
		<view class="history-modal" v-if="showHistory" @click.self="showHistory = false">
			<view class="history-content">
				<view class="history-header">
					<text class="history-title">历史会话</text>
					<view class="close-btn" @click="showHistory = false">
						<text>✕</text>
					</view>
				</view>
				<scroll-view class="history-list" scroll-y>
					<view 
						class="history-item"
						v-for="session in historySessions"
						:key="session.id"
						@click="loadSession(session.id)"
					>
						<view class="session-info">
							<text class="session-title">{{ session.title || '新对话' }}</text>
							<text class="session-time">{{ formatTime(session.updated_at) }}</text>
						</view>
						<view class="session-meta">
							<text class="session-count">{{ session.message_count }}条消息</text>
							<view class="delete-btn" @click.stop="deleteSession(session.id)">
								<text>🗑️</text>
							</view>
						</view>
					</view>
					<view class="empty-history" v-if="historySessions.length === 0">
						<text>暂无历史会话</text>
					</view>
				</scroll-view>
				<view class="new-chat-btn" @click="startNewChat">
					<text>+ 开始新对话</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { navigateBack } from '@/utils/navigation.js'
import { aiAPI } from '@/utils/api.js'

export default {
	data() {
		return {
			inputText: '',
			messages: [],
			presetQuestions: [],
			isLoading: false,
			scrollTop: 0,
			sessionId: null,
			showHistory: false,
			historySessions: []
		}
	},
	computed: {
		canSend() {
			return this.inputText.trim() && !this.isLoading
		}
	},
	onLoad() {
		this.loadPresetQuestions()
	},
	methods: {
		goBack() {
			navigateBack('/pages/teach/TeachHome')
		},
		
		// 加载预设问题
		async loadPresetQuestions() {
			try {
				const res = await aiAPI.getPresetQuestions()
				this.presetQuestions = res.questions || []
			} catch (e) {
				console.error('加载预设问题失败:', e)
				// 使用默认问题
				this.presetQuestions = [
					{ id: 1, icon: '🏐', question: '发球时手臂应该怎么挥？' },
					{ id: 2, icon: '💪', question: '扣球如何发力更有效？' },
					{ id: 3, icon: '🤲', question: '垫球手型应该怎么摆？' },
					{ id: 4, icon: '📋', question: '什么情况算持球犯规？' }
				]
			}
		},
		
		// 点击预设问题
		askPresetQuestion(question) {
			this.inputText = question
			this.sendMessage()
		},
		
		// 发送消息
		async sendMessage() {
			if (!this.canSend) return
			
			const userMessage = this.inputText.trim()
			this.inputText = ''
			
			// 添加用户消息
			this.messages.push({
				role: 'user',
				content: userMessage,
				time: this.getCurrentTime()
			})
			
			// 滚动到底部
			this.$nextTick(() => {
				this.scrollToBottom()
			})
			
			// 调用AI
			this.isLoading = true
			try {
				const res = await aiAPI.chat({
					message: userMessage,
					session_id: this.sessionId,
					context_type: 'coach'
				})
				
				if (res.success) {
					// 保存会话ID
					this.sessionId = res.session_id
					
					// 添加AI回复
					this.messages.push({
						role: 'assistant',
						content: res.ai_response,
						time: this.getCurrentTime()
					})
				} else {
					this.showError(res.message || 'AI回复失败')
				}
			} catch (e) {
				console.error('AI对话失败:', e)
				this.showError(e.message || '网络请求失败')
			} finally {
				this.isLoading = false
				this.$nextTick(() => {
					this.scrollToBottom()
				})
			}
		},
		
		// 加载历史会话列表
		async loadHistorySessions() {
			try {
				const res = await aiAPI.getSessions()
				this.historySessions = res.sessions || []
			} catch (e) {
				console.error('加载历史会话失败:', e)
			}
		},
		
		// 加载指定会话
		async loadSession(sessionId) {
			try {
				const res = await aiAPI.getSessionDetail(sessionId)
				this.sessionId = sessionId
				this.messages = res.messages.map(m => ({
					role: m.role,
					content: m.content,
					time: this.formatTime(m.created_at)
				}))
				this.showHistory = false
				this.$nextTick(() => {
					this.scrollToBottom()
				})
			} catch (e) {
				console.error('加载会话失败:', e)
				this.showError('加载会话失败')
			}
		},
		
		// 删除会话
		async deleteSession(sessionId) {
			uni.showModal({
				title: '确认删除',
				content: '确定要删除这个会话吗？',
				success: async (res) => {
					if (res.confirm) {
						try {
							await aiAPI.deleteSession(sessionId)
							// 从列表中移除
							this.historySessions = this.historySessions.filter(s => s.id !== sessionId)
							// 如果删除的是当前会话，清空
							if (this.sessionId === sessionId) {
								this.sessionId = null
								this.messages = []
							}
							uni.showToast({ title: '已删除', icon: 'success' })
						} catch (e) {
							this.showError('删除失败')
						}
					}
				}
			})
		},
		
		// 开始新对话
		startNewChat() {
			this.sessionId = null
			this.messages = []
			this.showHistory = false
		},
		
		// 加载更多历史
		loadMoreHistory() {
			// 可扩展：上拉加载更多历史消息
		},
		
		// 滚动到底部
		scrollToBottom() {
			this.scrollTop = this.scrollTop === 99999 ? 100000 : 99999
		},
		
		// 获取当前时间
		getCurrentTime() {
			const now = new Date()
			return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
		},
		
		// 格式化时间
		formatTime(timeStr) {
			if (!timeStr) return ''
			const date = new Date(timeStr)
			const now = new Date()
			const isToday = date.toDateString() === now.toDateString()
			
			if (isToday) {
				return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
			} else {
				return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
			}
		},
		
		// 显示错误
		showError(msg) {
			uni.showToast({
				title: msg,
				icon: 'none',
				duration: 2000
			})
		}
	},
	
	// 打开历史弹窗时加载
	watch: {
		showHistory(val) {
			if (val) {
				this.loadHistorySessions()
			}
		}
	}
}
</script>

<style scoped>
.ai-coach-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

/* 顶部标题栏 */
.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 30rpx;
	padding-top: calc(20rpx + env(safe-area-inset-top));
	background: rgba(255, 255, 255, 0.05);
	backdrop-filter: blur(10px);
}

.back-btn, .history-btn {
	width: 70rpx;
	height: 70rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.1);
}

.back-icon, .history-icon {
	font-size: 36rpx;
}

.title {
	font-size: 36rpx;
	font-weight: 700;
	color: var(--color-accent);
	letter-spacing: 2rpx;
}

/* 聊天区域 */
.chat-area {
	flex: 1;
	padding: 30rpx;
	overflow: hidden;
}

/* 欢迎区域 */
.welcome-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
}

.ai-avatar {
	font-size: 120rpx;
	margin-bottom: 30rpx;
	animation: none;
}

@keyframes bounce {
	0%, 100% { transform: translateY(0); }
	50% { transform: translateY(-15rpx); }
}

.welcome-title {
	font-size: 40rpx;
	font-weight: 700;
	color: #ffffff;
	margin-bottom: 16rpx;
}

.welcome-desc {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.6);
	text-align: center;
}

/* 预设问题 */
.preset-section {
	width: 100%;
	margin-top: 60rpx;
}

.preset-title {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.5);
	margin-bottom: 24rpx;
	display: block;
}

.preset-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.preset-item {
	display: flex;
	align-items: center;
	padding: 24rpx 30rpx;
	background: var(--color-line);
	border: 1rpx solid var(--color-line);
	border-radius: 20rpx;
	transition: transform 160ms ease, background-color 160ms ease;
}

.preset-item:active {
	background: var(--color-line);
	transform: scale(0.98);
}

.preset-icon {
	font-size: 36rpx;
	margin-right: 20rpx;
}

.preset-text {
	font-size: 28rpx;
	color: #ffffff;
}

/* 消息列表 */
.messages-container {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.message-item {
	display: flex;
	gap: 16rpx;
}

.message-item.user-message {
	flex-direction: row-reverse;
}

.message-avatar {
	width: 70rpx;
	height: 70rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 36rpx;
	flex-shrink: 0;
}

.user-message .message-avatar {
	background: var(--color-accent);
}

.message-content {
	max-width: 75%;
	display: flex;
	flex-direction: column;
}

.user-message .message-content {
	align-items: flex-end;
}

.message-bubble {
	padding: 24rpx 30rpx;
	border-radius: 24rpx;
	word-break: break-all;
}

.ai-message .message-bubble {
	background: rgba(255, 255, 255, 0.1);
	border-top-left-radius: 6rpx;
}

.user-message .message-bubble {
	background: var(--color-accent);
	border-top-right-radius: 6rpx;
}

.message-text {
	font-size: 28rpx;
	line-height: 1.6;
	white-space: pre-wrap;
}

.ai-message .message-text {
	color: #ffffff;
}

.user-message .message-text {
	color: #1a1a2e;
}

.message-time {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.4);
	margin-top: 8rpx;
}

/* 正在输入动画 */
.typing {
	padding: 20rpx 30rpx;
}

.typing-dots {
	display: flex;
	gap: 8rpx;
}

.dot {
	width: 12rpx;
	height: 12rpx;
	background: rgba(255, 255, 255, 0.6);
	border-radius: 50%;
	animation: typing 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
	0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
	30% { transform: translateY(-8rpx); opacity: 1; }
}

/* 底部输入区域 */
.input-area {
	display: flex;
	align-items: flex-end;
	gap: 20rpx;
	padding: 20rpx 30rpx;
	padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
	background: rgba(255, 255, 255, 0.05);
	backdrop-filter: blur(10px);
}

.input-wrapper {
	flex: 1;
	background: rgba(255, 255, 255, 0.1);
	border-radius: 24rpx;
	padding: 16rpx 24rpx;
	border: 1rpx solid var(--color-line);
}

.input-field {
	width: 100%;
	min-height: 40rpx;
	max-height: 200rpx;
	font-size: 28rpx;
	color: #ffffff;
	background: transparent;
}

.send-btn {
	width: 80rpx;
	height: 80rpx;
	background: var(--color-accent);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: transform 160ms ease, background-color 160ms ease;
}

.send-btn:active {
	transform: scale(0.95);
}

.send-btn.disabled {
	background: rgba(255, 255, 255, 0.2);
	opacity: 0.5;
}

.send-icon {
	font-size: 36rpx;
}

/* 历史会话弹窗 */
.history-modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: flex-end;
	z-index: 1000;
}

.history-content {
	width: 100%;
	max-height: 70vh;
	background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
	border-top-left-radius: 40rpx;
	border-top-right-radius: 40rpx;
	padding: 30rpx;
	padding-bottom: calc(30rpx + env(safe-area-inset-bottom));
	display: flex;
	flex-direction: column;
}

.history-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-bottom: 24rpx;
	border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
}

.history-title {
	font-size: 32rpx;
	font-weight: 700;
	color: var(--color-accent);
}

.close-btn {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	color: rgba(255, 255, 255, 0.6);
}

.history-list {
	flex: 1;
	margin: 20rpx 0;
	max-height: 50vh;
}

.history-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx;
	background: rgba(255, 255, 255, 0.05);
	border-radius: 16rpx;
	margin-bottom: 16rpx;
}

.history-item:active {
	background: rgba(255, 255, 255, 0.1);
}

.session-info {
	flex: 1;
}

.session-title {
	font-size: 28rpx;
	color: #ffffff;
	display: block;
	margin-bottom: 8rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	max-width: 400rpx;
}

.session-time {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.4);
}

.session-meta {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.session-count {
	font-size: 22rpx;
	color: var(--color-line);
}

.delete-btn {
	padding: 12rpx;
	font-size: 28rpx;
}

.empty-history {
	text-align: center;
	padding: 60rpx;
	color: rgba(255, 255, 255, 0.4);
	font-size: 28rpx;
}

.new-chat-btn {
	background: var(--color-accent);
	padding: 24rpx;
	border-radius: 24rpx;
	text-align: center;
}

.new-chat-btn text {
	font-size: 30rpx;
	font-weight: 600;
	color: #1a1a2e;
}

.ai-coach-container { height: 100vh; height: 100dvh; background: var(--color-bg); color: var(--color-ink); }
.header { background: white; border-bottom: 1rpx solid var(--color-line); backdrop-filter: none; }
.title, .history-title { color: var(--color-ink); letter-spacing: 0; }
.back-btn, .history-btn { background: var(--color-bg); }
.chat-area { min-height: 0; padding: 24rpx 32rpx; }
.welcome-section { padding: 48rpx 0; }
.ai-avatar { width: 100rpx; height: 100rpx; padding: 22rpx; background: var(--color-accent-soft); border-radius: 28rpx; animation: none; }
.welcome-title { color: var(--color-ink); font-size: 36rpx; }
.welcome-desc, .preset-title, .message-time, .session-time, .session-count, .empty-history, .close-btn { color: var(--color-muted); }
.welcome-desc { font-size: 25rpx; line-height: 1.7; }
.preset-item { background: white; border-color: var(--color-line); }
.preset-item:active { background: var(--color-accent-soft); }
.preset-text, .session-title, .input-field, .ai-message .message-text { color: var(--color-ink); }
.ai-message .message-bubble { background: white; border: 1rpx solid var(--color-line); }
.user-message .message-bubble { background: #f7e8dc; }
.user-message .message-text { color: var(--color-ink); }
.message-avatar { background: #e9ede6; }
.user-message .message-avatar { background: #f7e8dc; }
.dot { background: var(--color-muted); }
.input-area { background: white; border-top: 1rpx solid var(--color-line); backdrop-filter: none; }
.input-wrapper { background: var(--color-bg); border-color: var(--color-line); min-width: 0; }
.send-btn { background: var(--color-accent); border-radius: 20rpx; flex-shrink: 0; }
.send-btn.disabled { background: #dce2d8; opacity: 1; }
.send-icon { width: 36rpx; height: 36rpx; }
.history-content { background: white; }
.history-header { border-color: var(--color-line); }
.history-item { background: var(--color-bg); }
.new-chat-btn { background: var(--color-accent); }
.new-chat-btn text { color: white; }

.preset-icon { width: 30rpx; height: 30rpx; flex-shrink: 0; }
.back-btn, .history-btn, .send-btn { margin: 0; padding: 0; line-height: 1; min-width: 44px; min-height: 44px; }
</style>

