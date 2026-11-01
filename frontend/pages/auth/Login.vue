<template>
	<view class="login-container">
		<view class="login-header">
            <text class="page-kicker">YOUR NEXT CHAPTER</text>
			<image class="logo" src="/static/icons/ball-volleyball-active.png" mode="aspectFit"></image>
			<text class="app-title">排球少年·启程</text>
			<text class="welcome-text">欢迎回来</text>
		</view>
		
		<!-- 登录方式切换 -->
		<view class="login-tabs">
			<view 
				class="tab-item" 
				:class="{ active: loginType === 'password' }"
				@click="switchLoginType('password')"
			>
				<text>账号密码登录</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: loginType === 'sms' }"
				@click="switchLoginType('sms')"
			>
				<text>手机验证码登录</text>
			</view>
		</view>
		
		<view class="login-form">
			<!-- 账号密码登录表单 -->
			<template v-if="loginType === 'password'">
				<view class="form-item">
					<text class="label">用户名</text>
					<input 
						class="input" 
						v-model="passwordForm.username" 
						type="text"
						maxlength="50"
						placeholder="请输入用户名"
						placeholder-style="color: #737b75"
					/>
				</view>
				
				<view class="form-item">
					<text class="label">密码</text>
					<input 
						class="input" 
						v-model="passwordForm.password" 
						type="password"
						maxlength="50"
						placeholder="请输入密码"
						placeholder-style="color: #737b75"
					/>
				</view>
				
				<button class="login-btn" :loading="loading" @click="handlePasswordLogin">登录</button>
				
				<view class="links">
					<text class="link" @click="goToRegister">没有账号？立即注册</text>
					<text class="link" @click="goToForgotPassword">忘记密码</text>
				</view>
			</template>
			
			<!-- 手机验证码登录表单 -->
			<template v-else>
				<view class="form-item">
					<text class="label">手机号</text>
					<input 
						class="input" 
						v-model="smsForm.phone" 
						type="number"
						maxlength="11"
						placeholder="请输入手机号"
						placeholder-style="color: #737b75"
					/>
				</view>
				
				<view class="form-item">
					<text class="label">验证码</text>
					<view class="code-input-wrapper">
						<input 
							class="input code-input" 
							v-model="smsForm.code" 
							type="number"
							maxlength="6"
							placeholder="请输入验证码"
							placeholder-style="color: #737b75"
						/>
						<button 
							class="send-code-btn" 
							:disabled="countdown > 0 || sendingCode"
							:loading="sendingCode"
							@click="handleSendCode"
						>
							{{ countdown > 0 ? `${countdown}s后重发` : '获取验证码' }}
						</button>
					</view>
				</view>
				
				<button class="login-btn" :loading="loading" @click="handleSmsLogin">登录</button>
				
				<view class="tips">
					<text class="tips-text">未注册的手机号将自动创建账号</text>
				</view>
			</template>
		</view>
	</view>
</template>

<script>
	import { authAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loginType: 'password', // 'password' 或 'sms'
				passwordForm: {
					username: '',
					password: ''
				},
				smsForm: {
					phone: '',
					code: ''
				},
				loading: false,
				sendingCode: false,
				countdown: 0,
				timer: null
			}
		},
		onUnload() {
			if (this.timer) {
				clearInterval(this.timer)
			}
		},
		methods: {
			// 切换登录方式
			switchLoginType(type) {
				this.loginType = type
			},
			
			// 验证手机号格式
			validatePhone(phone) {
				if (!phone || phone.length !== 11) {
					return false
				}
				return /^1[3-9]\d{9}$/.test(phone)
			},
			
			// 发送验证码
			async handleSendCode() {
				const phone = String(this.smsForm.phone || '').trim()
				
				if (!this.validatePhone(phone)) {
					uni.showToast({
						title: '请输入正确的手机号',
						icon: 'none'
					})
					return
				}
				
				this.sendingCode = true
				
				try {
					await authAPI.sendSmsCode(phone, 'login')
					
					uni.showToast({
						title: '验证码已发送',
						icon: 'success'
					})
					
					this.countdown = 60
					this.timer = setInterval(() => {
						this.countdown--
						if (this.countdown <= 0) {
							clearInterval(this.timer)
							this.timer = null
						}
					}, 1000)
					
				} catch (error) {
					uni.showToast({
						title: error.message || '发送失败，请重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.sendingCode = false
				}
			},
			
			// 账号密码登录
			async handlePasswordLogin() {
				const username = String(this.passwordForm.username || '').trim()
				const password = String(this.passwordForm.password || '').trim()
				
				if (!username) {
					uni.showToast({
						title: '请输入用户名',
						icon: 'none'
					})
					return
				}
				
				if (!password) {
					uni.showToast({
						title: '请输入密码',
						icon: 'none'
					})
					return
				}
				
				if (password.length < 6) {
					uni.showToast({
						title: '密码长度不能少于6位',
						icon: 'none'
					})
					return
				}
				
				this.loading = true
				
				try {
					const res = await authAPI.login({
						username: username,
						password: password
					})
					
					uni.setStorageSync('token', res.access_token)
					uni.setStorageSync('userInfo', res.user)
					
					uni.showToast({
						title: '登录成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/home/Home'
						})
					}, 1500)
					
				} catch (error) {
					uni.showToast({
						title: error.message || '登录失败，请重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			
			// 手机验证码登录
			async handleSmsLogin() {
				const phone = String(this.smsForm.phone || '').trim()
				const code = String(this.smsForm.code || '').trim()
				
				if (!this.validatePhone(phone)) {
					uni.showToast({
						title: '请输入正确的手机号',
						icon: 'none'
					})
					return
				}
				
				if (!code || code.length < 4) {
					uni.showToast({
						title: '请输入验证码',
						icon: 'none'
					})
					return
				}
				
				this.loading = true
				
				try {
					const res = await authAPI.smsLogin({
						phone: phone,
						code: code
					})
					
					uni.setStorageSync('token', res.access_token)
					uni.setStorageSync('userInfo', res.user)
					
					uni.showToast({
						title: '登录成功',
						icon: 'success'
					})
					
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/home/Home'
						})
					}, 1500)
					
				} catch (error) {
					uni.showToast({
						title: error.message || '登录失败，请重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			
			// 跳转到注册页面
			goToRegister() {
				uni.navigateTo({
					url: '/pages/auth/Register'
				})
			},
			
			// 跳转到忘记密码页面
			goToForgotPassword() {
				uni.navigateTo({
					url: '/pages/auth/ForgotPassword'
				})
			}
		}
	}
</script>

<style scoped>
	.login-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 60rpx 40rpx;
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	
	.login-header {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 60rpx;
		margin-top: 60rpx;
	}
	
	.logo {
		width: 140rpx;
		height: 140rpx;
		margin-bottom: 30rpx;
	}
	
	.app-title {
		font-size: 40rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 16rpx;
		letter-spacing: 2rpx;
	}
	
	.welcome-text {
		font-size: 26rpx;
		color: var(--color-muted);
	}
	
	/* 登录方式切换标签 */
	.login-tabs {
		display: flex;
		background: #FFFFFF;
		border-radius: 16rpx;
		padding: 8rpx;
		margin-bottom: 50rpx;
		box-shadow: var(--shadow-card);
	}
	
	.tab-item {
		flex: 1;
		height: 72rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 12rpx;
		font-size: 26rpx;
		color: var(--color-muted);
		transition: transform 160ms ease, background-color 160ms ease;
	}
	
	.tab-item.active {
		background: var(--color-accent);
		color: #FFFFFF;
		font-weight: 600;
	}
	
	.login-form {
		flex: 1;
	}
	
	.form-item {
		margin-bottom: 36rpx;
	}
	
	.label {
		display: block;
		font-size: 28rpx;
		color: var(--color-ink);
		margin-bottom: 16rpx;
		font-weight: 600;
	}
	
	.input {
		width: 100%;
		height: 88rpx;
		background: #FFFFFF;
		border-radius: 16rpx;
		padding: 0 30rpx;
		font-size: 28rpx;
		color: var(--color-ink);
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
		box-sizing: border-box;
	}
	
	.code-input-wrapper {
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	
	.code-input {
		flex: 1;
	}
	
	.send-code-btn {
		width: 220rpx;
		height: 88rpx;
		background: linear-gradient(135deg, var(--color-accent) 0%, #FF5252 100%);
		border-radius: 16rpx;
		color: #FFFFFF;
		font-size: 26rpx;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		padding: 0;
		flex-shrink: 0;
	}
	
	.send-code-btn::after {
		border: none;
	}
	
	.send-code-btn[disabled] {
		background: #CCCCCC;
		color: #FFFFFF;
	}
	
	.login-btn {
		width: 100%;
		height: 88rpx;
		background: var(--color-accent);
		border-radius: 16rpx;
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: var(--shadow-card);
		margin-top: 50rpx;
		margin-bottom: 30rpx;
		border: none;
	}
	
	.login-btn::after {
		border: none;
	}
	
	.tips {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-top: 30rpx;
	}
	
	.tips-text {
		font-size: 24rpx;
		color: var(--color-muted);
	}
	
	/* 链接样式 */
	.links {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 30rpx;
		padding: 0 10rpx;
	}
	
	.link {
		font-size: 26rpx;
		color: var(--color-accent);
	}

.login-container { padding: 48rpx 44rpx; max-width: 540px; margin: 0 auto; }
.login-header { align-items: flex-start; margin-top: 16rpx; margin-bottom: 44rpx; position: relative; }
.logo { width: 84rpx; height: 84rpx; margin: 4rpx 0 24rpx; border-radius: 20rpx; }
.app-title { font-size: 46rpx; letter-spacing: -1rpx; line-height: 1.3; }
.welcome-text { font-size: 26rpx; color: var(--color-muted); margin-top: 8rpx; }
.login-tabs { background: #e9ede6; box-shadow: none; margin-bottom: 36rpx; }
.tab-item.active { background: white; color: var(--color-ink); box-shadow: 0 3rpx 8rpx rgba(30,40,30,.06); }
.input { height: 96rpx; border: 1rpx solid #dce2d8; box-shadow: none; border-radius: 16rpx; }
.input:focus-within { border-color: var(--color-accent); }
.label { font-size: 25rpx; margin-bottom: 12rpx; }
.form-item { margin-bottom: 30rpx; }
.code-input { min-width: 0; }
.send-code-btn { background: var(--color-accent-soft); color: var(--color-accent); height: 96rpx; width: 206rpx; }
.login-btn, .register-btn, .reset-btn { background: var(--color-accent); color: white; height: 94rpx; box-shadow: none; border-radius: 16rpx; margin-top: 36rpx; }
.link { color: var(--color-accent); font-size: 24rpx; }
.links { flex-wrap: wrap; gap: 20rpx; }


.logo { background: var(--color-accent-soft); padding: 14rpx; }
.user-avatar { background: var(--color-accent-soft); padding: 14rpx; }
</style>
