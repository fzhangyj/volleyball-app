<template>
	<view class="settings-container">
		<!-- 用户信息编辑区 -->
		<view class="info-section">
			<view class="avatar-section">
				<image class="avatar" :src="avatarUrl" mode="aspectFill"></image>
				<button 
					class="change-avatar-btn" 
					@click="changeAvatar"
					:loading="uploadingAvatar"
					:disabled="uploadingAvatar"
				>
					{{ uploadingAvatar ? '上传中...' : '更换头像' }}
				</button>
			</view>
			
			<view class="form-item">
				<text class="label">用户名</text>
				<input 
					class="input" 
					v-model="formData.username" 
					placeholder="请输入用户名"
					maxlength="50"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">手机号</text>
				<input 
					class="input" 
					v-model="formData.phone" 
					placeholder="请输入手机号"
					type="number"
					maxlength="11"
					:disabled="true"
				/>
				<text class="hint">手机号不可修改</text>
			</view>
		</view>
		
		<!-- 其他设置 -->
		<view class="settings-section">
			<view class="settings-item" @click="goToAbout">
				<text class="settings-label">关于我们</text>
				<text class="settings-arrow">></text>
			</view>
			<view class="settings-item" @click="goToFeedback">
				<text class="settings-label">意见反馈</text>
				<text class="settings-arrow">></text>
			</view>
		</view>
		
		<!-- 保存按钮 -->
		<button class="save-btn" :loading="saving" @click="saveSettings">保存</button>
	</view>
</template>

<script>
import { navigateBack } from '@/utils/navigation.js'
	import { authAPI } from '@/utils/api.js'
	
	import { BASE_URL } from '@/utils/config.js'
	
	export default {
		data() {
			return {
				avatarUrl: '/static/icons/ball-volleyball-active.png',
				formData: {
					username: '',
					phone: ''
				},
				saving: false,
				uploadingAvatar: false,
				tempAvatarPath: null
			}
		},
		onLoad() {
			this.loadUserInfo()
		},
		methods: {
			async loadUserInfo() {
				try {
					const userInfo = await authAPI.getCurrentUser()
					if (userInfo) {
						this.formData.username = userInfo.username || ''
						this.formData.phone = userInfo.phone || ''
						if (userInfo.avatar) {
							this.avatarUrl = `${BASE_URL}/uploads/${userInfo.avatar}`
						}
						uni.setStorageSync('userInfo', userInfo)
					}
				} catch (error) {
					console.error('加载用户信息失败:', error)
					const userInfo = uni.getStorageSync('userInfo')
					if (userInfo) {
						this.formData.username = userInfo.username || ''
						this.formData.phone = userInfo.phone || ''
						if (userInfo.avatar) {
							this.avatarUrl = `${BASE_URL}/uploads/${userInfo.avatar}`
						}
					}
				}
			},
			
			changeAvatar() {
				uni.chooseImage({
					count: 1,
					sizeType: ['compressed'],
					sourceType: ['album', 'camera'],
					success: async (res) => {
						const tempFilePath = res.tempFilePaths[0]
						this.tempAvatarPath = tempFilePath
						this.avatarUrl = tempFilePath
						
						this.uploadingAvatar = true
						try {
							const userInfo = await authAPI.uploadAvatar(tempFilePath)
							if (userInfo && userInfo.avatar) {
								this.avatarUrl = `${BASE_URL}/uploads/${userInfo.avatar}`
								uni.setStorageSync('userInfo', userInfo)
								uni.showToast({
									title: '头像上传成功',
									icon: 'success'
								})
							}
						} catch (error) {
							console.error('上传头像失败:', error)
							uni.showToast({
								title: error.message || '上传失败，请重试',
								icon: 'none',
								duration: 2000
							})
							const userInfo = uni.getStorageSync('userInfo')
							if (userInfo && userInfo.avatar) {
								this.avatarUrl = `${BASE_URL}/uploads/${userInfo.avatar}`
							}
						} finally {
							this.uploadingAvatar = false
						}
					},
					fail: (err) => {
						console.error('选择图片失败:', err)
						uni.showToast({
							title: '选择图片失败',
							icon: 'none'
						})
					}
				})
			},
			
			async saveSettings() {
				if (!this.formData.username.trim()) {
					uni.showToast({
						title: '请输入用户名',
						icon: 'none'
					})
					return
				}
				
				this.saving = true
				try {
					const userInfo = await authAPI.updateProfile({
						username: this.formData.username.trim()
					})
					
					if (userInfo) {
						uni.setStorageSync('userInfo', userInfo)
						uni.showToast({
							title: '保存成功',
							icon: 'success'
						})
						
						setTimeout(() => {
							navigateBack('/pages/profile/Profile')
						}, 1500)
					}
				} catch (error) {
					uni.showToast({
						title: error.message || '保存失败',
						icon: 'none'
					})
				} finally {
					this.saving = false
				}
			},
			
			goToAbout() {
				uni.showModal({
					title: '关于我们',
					content: '排球少年·启程\n一个专业的排球教学APP\n帮助您提升排球技能',
					showCancel: false
				})
			},
			
			goToFeedback() {
				uni.showModal({
					title: '意见反馈',
					content: '如有任何意见或建议，请联系我们',
					showCancel: false
				})
			}
		}
	}
</script>

<style scoped>
	.settings-container {
		min-height: calc(100vh - 100px);
		min-height: calc(100dvh - 100px);
		background: var(--color-bg);
		padding: 30rpx;
		padding-bottom: 100rpx;
	}
	
	.info-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 45rpx;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}
	
	.avatar-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 50rpx;
	}
	
	.avatar {
		width: 200rpx;
		height: 200rpx;
		border-radius: 50%;
		margin-bottom: 30rpx;
		border: 5rpx solid;
		border-image: var(--color-accent) 1;
		box-shadow: var(--shadow-card);
	}
	
	.change-avatar-btn {
		font-size: 28rpx;
		color: var(--color-accent);
		font-weight: 600;
		background: transparent;
		border: none;
		padding: 0;
		margin-top: 20rpx;
	}
	
	.change-avatar-btn::after {
		border: none;
	}
	
	.change-avatar-btn[disabled] {
		opacity: 0.6;
	}
	
	.form-item {
		margin-bottom: 40rpx;
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
	
	.input[disabled] {
		background: #F5F5F5;
		color: var(--color-muted);
	}
	
	.hint {
		display: block;
		font-size: 24rpx;
		color: var(--color-muted);
		margin-top: 12rpx;
	}
	
	.settings-section {
		background: var(--color-surface);
		border-radius: 28rpx;
		padding: 0 35rpx;
		margin-bottom: 35rpx;
		box-shadow: var(--shadow-card);
		border: 1rpx solid var(--color-line);
	}
	
	.settings-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 35rpx 0;
		border-bottom: 1rpx solid var(--color-line);
	}
	
	.settings-item:last-child {
		border-bottom: none;
	}
	
	.settings-label {
		font-size: 30rpx;
		color: var(--color-ink);
		font-weight: 500;
	}
	
	.settings-arrow {
		font-size: 36rpx;
		color: var(--color-muted);
		font-weight: 300;
	}
	
	.save-btn {
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
		border: none;
	}
	
	.save-btn::after {
		border: none;
	}

.save-btn { background: var(--color-accent); color: white; box-shadow: none; }


.logo { background: var(--color-accent-soft); padding: 14rpx; }
.user-avatar { background: var(--color-accent-soft); padding: 14rpx; }
</style>

