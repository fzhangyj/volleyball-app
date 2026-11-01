<template>
	<view class="forgot-container">
		<view class="forgot-header">
            <text class="page-kicker">YOUR NEXT CHAPTER</text>
			<image class="logo" src="/static/icons/ball-volleyball-active.png" mode="aspectFit"></image>
			<text class="app-title">忘记密码</text>
			<text class="welcome-text">通过手机验证码重置密码</text>
		</view>
		
		<view class="forgot-form">
			<view class="form-item">
				<text class="label">手机号</text>
				<input 
					class="input" 
					v-model="formData.phone" 
					type="number"
					placeholder="请输入注册手机号"
					placeholder-style="color: #737b75"
					maxlength="11"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">验证码</text>
				<view class="code-input-wrapper">
					<input 
						class="input code-input" 
						v-model="formData.smsCode" 
						type="number"
						placeholder="请输入6位验证码"
						placeholder-style="color: #737b75"
						maxlength="6"
					/>
					<button 
						class="send-code-btn" 
						:disabled="countdown > 0"
						@click="handleSendCode"
					>
						{{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
					</button>
				</view>
			</view>
			
			<view class="form-item">
				<text class="label">新密码</text>
				<input 
					class="input" 
					v-model="formData.newPassword" 
					password
					placeholder="请输入新密码（至少6位）"
					placeholder-style="color: #737b75"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">确认密码</text>
				<input 
					class="input" 
					v-model="formData.confirmPassword" 
					password
					placeholder="请再次输入新密码"
					placeholder-style="color: #737b75"
				/>
			</view>
			
			<button class="submit-btn" :loading="loading" @click="handleSubmit">重置密码</button>
			
			<view class="login-link">
				<text class="link-text">想起密码了？</text>
				<text class="link-btn" @click="goToLogin">返回登录</text>
			</view>
		</view>
	</view>
</template>

<script>
import { navigateBack } from '@/utils/navigation.js'
	import { authAPI } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				formData: {
					phone: '',
					smsCode: '',
					newPassword: '',
					confirmPassword: ''
				},
				loading: false,
				countdown: 0,
				timer: null
			}
		},
		beforeDestroy() {
			// 清除定时器
			if (this.timer) {
				clearInterval(this.timer)
			}
		},
		methods: {
			// 发送验证码
			async handleSendCode() {
				// 验证手机号
				if (!this.formData.phone) {
					uni.showToast({
						title: '请输入手机号',
						icon: 'none'
					})
					return
				}
				
				if (!/^1[3-9]\d{9}$/.test(this.formData.phone)) {
					uni.showToast({
						title: '手机号格式不正确',
						icon: 'none'
					})
					return
				}
				
				try {
					// 调用发送验证码接口，场景为reset_password
					await authAPI.sendSmsCode(this.formData.phone, 'reset_password')
					
					uni.showToast({
						title: '验证码已发送',
						icon: 'success'
					})
					
					// 60秒倒计时防止重复发送
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
				}
			},
			
			async handleSubmit() {
				// 表单验证
				if (!this.formData.phone) {
					uni.showToast({
						title: '请输入手机号',
						icon: 'none'
					})
					return
				}
				
				if (!/^1[3-9]\d{9}$/.test(this.formData.phone)) {
					uni.showToast({
						title: '手机号格式不正确',
						icon: 'none'
					})
					return
				}
				
				if (!this.formData.smsCode) {
					uni.showToast({
						title: '请输入验证码',
						icon: 'none'
					})
					return
				}
				
				if (this.formData.smsCode.length !== 6) {
					uni.showToast({
						title: '请输入6位验证码',
						icon: 'none'
					})
					return
				}
				
				if (!this.formData.newPassword.trim()) {
					uni.showToast({
						title: '请输入新密码',
						icon: 'none'
					})
					return
				}
				
				if (this.formData.newPassword.length < 6) {
					uni.showToast({
						title: '密码长度至少6位',
						icon: 'none'
					})
					return
				}
				
				if (this.formData.newPassword !== this.formData.confirmPassword) {
					uni.showToast({
						title: '两次输入的密码不一致',
						icon: 'none'
					})
					return
				}
				
				this.loading = true
				
				try {
					// 调用重置密码接口
					await authAPI.resetPasswordWithSms({
						phone: this.formData.phone,
						sms_code: this.formData.smsCode,
						new_password: this.formData.newPassword
					})
					
					uni.showToast({
						title: '密码重置成功',
						icon: 'success'
					})
					
					// 延迟跳转到登录页
					setTimeout(() => {
						navigateBack('/pages/auth/Login', false)
					}, 1500)
					
				} catch (error) {
					uni.showToast({
						title: error.message || '重置失败，请重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			
			goToLogin() {
				// 使用redirectTo确保能跳转到登录页
				uni.redirectTo({
					url: '/pages/auth/Login'
				})
			}
		}
	}
</script>

<style scoped>
	.forgot-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 60rpx 40rpx;
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	
	.forgot-header {
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
		font-size: 42rpx;
		font-weight: 700;
		color: var(--color-ink);
		margin-bottom: 20rpx;
		letter-spacing: 2rpx;
	}
	
	.welcome-text {
		font-size: 28rpx;
		color: var(--color-muted);
		text-align: center;
	}
	
	.forgot-form {
		flex: 1;
	}
	
	.form-item {
		margin-bottom: 35rpx;
	}
	
	.label {
		display: block;
		font-size: 28rpx;
		color: var(--color-ink);
		margin-bottom: 20rpx;
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
		width: 200rpx;
		height: 88rpx;
		background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
		border-radius: 16rpx;
		color: #FFFFFF;
		font-size: 26rpx;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		padding: 0;
	}
	
	.send-code-btn[disabled] {
		background: #CCCCCC;
		color: #FFFFFF;
	}
	
	.send-code-btn::after {
		border: none;
	}
	
	.submit-btn {
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
		margin-top: 40rpx;
		margin-bottom: 40rpx;
		border: none;
	}
	
	.submit-btn::after {
		border: none;
	}
	
	.login-link {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-top: 40rpx;
	}
	
	.link-text {
		font-size: 26rpx;
		color: var(--color-muted);
		margin-right: 10rpx;
	}
	
	.link-btn {
		font-size: 26rpx;
		color: var(--color-accent);
		font-weight: 600;
	}

.forgot-container { padding: 48rpx 44rpx; max-width: 540px; margin: 0 auto; }
.forgot-header { align-items: flex-start; margin-top: 16rpx; margin-bottom: 44rpx; position: relative; }
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
