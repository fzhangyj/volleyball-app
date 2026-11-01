<template>
  <view class="teach-home-container">
    <view class="page-heading"><text class="page-kicker">TRAIN. PLAY. GROW.</text><text class="page-title">把热爱，练成实力。</text><text class="page-subtitle">找到自己的节奏，一次专注一个小进步。</text></view>
    <button role="button" tabindex="0" class="coach-card" @keydown.enter.prevent="goToPage('/pages/teach/TeachAI')" @keydown.space.prevent="goToPage('/pages/teach/TeachAI')" @click="goToPage('/pages/teach/TeachAI')">
      <view class="coach-top"><image class="coach-icon" src="/static/icons/sparkles-active.png" /><text class="coach-label">你的专属练习搭档</text><image class="coach-arrow" src="/static/icons/arrow-up-right.png" /></view>
      <text class="coach-title">AI教练，陪你找到突破口</text><text class="coach-desc">动作不懂、规则不熟？把问题交给教练。</text>
      <view class="coach-link">向教练提问<image class="ui-icon" src="/static/icons/arrow-right-active.png" /></view>
    </button>
    <view class="training-heading"><text class="section-title">今天，练点什么？</text><text class="section-desc">从基础出发，让进步有迹可循</text></view>
    <view class="grid-section">
      <button role="button" tabindex="0" class="grid-item" v-for="(item, index) in gridList" :key="item.path" @keydown.enter.prevent="goToPage(item.path)" @keydown.space.prevent="goToPage(item.path)" @click="goToPage(item.path)">
        <view class="grid-top"><image class="grid-icon" :src="'/static/icons/' + item.icon + '.png'" /><text class="grid-number">0{{ index + 1 }}</text></view>
        <text class="grid-title">{{ item.title }}</text><text class="grid-desc">{{ item.desc }}</text><view class="grid-link">{{ item.action }}<image class="link-arrow" src="/static/icons/arrow-right-muted.png" /></view>
      </button>
    </view>
    <view class="training-note"><image class="ui-icon" src="/static/icons/ball-volleyball-muted.png" /><text>不必一开始就很厉害，先开始就好。</text></view>
  </view>
</template>
<script>
export default {
  data() { return { gridList: [
    { icon: 'book', title: '规则', desc: '读懂轮转、得分与场上位置', action: '打好基础', path: '/pages/teach/TeachRule' },
    { icon: 'player-play', title: '上课', desc: '跟着视频，把动作拆开练', action: '选择课程', path: '/pages/teach/TeachCourse' },
    { icon: 'bolt', title: '技能', desc: '垫球、传球、发球，逐个突破', action: '专项提升', path: '/pages/teach/TeachSkill' },
    { icon: 'target', title: '反应力', desc: '练习判断，让反应快一点', action: '开始挑战', path: '/pages/teach/TeachReact' }
  ] } },
  methods: { goToPage(url) { uni.navigateTo({ url, fail: () => uni.showToast({ title: '页面暂时无法打开，请重试', icon: 'none' }) }) } }
}
</script>
<style scoped>
.teach-home-container { padding: 40rpx 36rpx; background: var(--color-bg); }
.coach-card { width: 100%; margin: 0; padding: 30rpx; background: #f7e8dc; border: 1rpx solid #eedbca; border-radius: 26rpx; text-align: left; line-height: 1.5; }
.coach-top { display: flex; align-items: center; gap: 16rpx; margin-bottom: 28rpx; }
.coach-icon { width: 44rpx; height: 44rpx; }
.coach-label { font-size: 24rpx; color: #884428; flex: 1; }
.coach-arrow { width: 36rpx; height: 36rpx; }
.coach-title { font-size: 34rpx; font-weight: 750; display: block; color: var(--color-ink); }
.coach-desc { display: block; font-size: 24rpx; color: #735c4d; margin-top: 12rpx; }
.coach-link { display: flex; align-items: center; gap: 14rpx; font-size: 25rpx; color: var(--color-accent); margin-top: 26rpx; font-weight: 650; }
.coach-link .ui-icon { width: 32rpx; height: 32rpx; }
.training-heading { margin: 40rpx 0 24rpx; }
.section-title { display: block; font-size: 34rpx; font-weight: 700; }
.section-desc { display: block; font-size: 24rpx; color: var(--color-muted); margin-top: 8rpx; }
.grid-section { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 20rpx; }
.grid-item { width: 100%; padding: 28rpx; margin: 0; text-align: left; background: white; border: 1rpx solid var(--color-line); border-radius: 24rpx; line-height: 1.5; }
.grid-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24rpx; }
.grid-icon { width: 46rpx; height: 46rpx; }
.grid-number { color: #767e75; font-size: 23rpx; font-variant-numeric: tabular-nums; }
.grid-title { display: block; font-size: 32rpx; font-weight: 700; color: var(--color-ink); }
.grid-desc { display: block; color: var(--color-muted); font-size: 23rpx; margin-top: 10rpx; min-height: 70rpx; }
.grid-link { display: flex; align-items: center; justify-content: space-between; color: var(--color-muted); font-size: 22rpx; margin-top: 24rpx; padding-top: 20rpx; border-top: 1rpx solid var(--color-line); }
.link-arrow { width: 30rpx; height: 30rpx; }
.training-note { display: flex; align-items: center; justify-content: center; gap: 14rpx; margin-top: 36rpx; color: var(--color-muted); font-size: 23rpx; }
.training-note .ui-icon { width: 30rpx; height: 30rpx; }
.grid-item:active, .coach-card:active { transform: scale(.985); }
@media (min-width: 768px) { .teach-home-container { padding: 40px; } .grid-section { grid-template-columns: repeat(4, minmax(0,1fr)); } }
</style>
