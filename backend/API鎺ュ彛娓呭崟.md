# 排球APP API接口清单

## 一、认证相关 API (已完成)
### 基础路径: `/api/v1/auth`

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/register` | 用户注册 | ✅ 已完成 |
| POST | `/login` | 账号密码登录 | ✅ 已完成 |
| POST | `/sms-login` | 手机验证码登录 | ✅ 已完成 |
| POST | `/send-sms-code` | 发送短信验证码 | ✅ 已完成 |
| POST | `/forgot-password` | 忘记密码（生成重置token） | ✅ 已完成 |
| POST | `/reset-password` | 重置密码 | ✅ 已完成 |
| GET | `/me` | 获取当前用户信息 | ✅ 已完成 |
| PUT | `/me` | 更新用户资料 | ✅ 已完成 |
| POST | `/me/avatar` | 上传用户头像 | ✅ 已完成 |

---

## 二、课程相关 API (已完成)
### 基础路径: `/api/v1/courses`

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/` | 获取课程列表（支持分页、分类、技能类型、搜索） | ✅ 已完成 |
| GET | `/{course_id}` | 获取课程详情 | ✅ 已完成 |
| GET | `/categories/list` | 获取课程分类列表 | ✅ 已完成 |
| POST | `/favorites` | 收藏课程/加入学习计划 | ✅ 已完成 |
| GET | `/favorites/list` | 获取收藏列表 | ✅ 已完成 |
| DELETE | `/favorites/{course_id}` | 取消收藏 | ✅ 已完成 |
| GET | `/studying/list` | 获取学习中的课程列表 | ✅ 已完成 |
| POST | `/progress` | 创建/更新学习进度 | ✅ 已完成 |
| GET | `/progress/list` | 获取学习进度列表 | ✅ 已完成 |
| GET | `/statistics` | 获取学习统计信息 | ✅ 已完成 |

---

## 三、Banner管理 API (需新增)
### 基础路径: `/api/v1/banners`

| 方法 | 路径 | 说明 | 用途 |
|------|------|------|------|
| GET | `/` | 获取Banner列表 | 首页轮播图展示 |
| GET | `/{banner_id}` | 获取Banner详情 | 查看Banner详情 |
| POST | `/` | 创建Banner（管理员） | 后台管理用 |
| PUT | `/{banner_id}` | 更新Banner（管理员） | 后台管理用 |
| DELETE | `/{banner_id}` | 删除Banner（管理员） | 后台管理用 |

---

## 四、规则内容管理 API (需新增)
### 基础路径: `/api/v1/rules`

| 方法 | 路径 | 说明 | 用途 |
|------|------|------|------|
| GET | `/content` | 获取规则内容 | TeachRule.vue 显示规则内容 |
| POST | `/progress` | 保存规则学习进度 | TeachRule.vue "我学会了"功能 |

---

## 五、反应力训练 API (需新增)
### 基础路径: `/api/v1/training`

| 方法 | 路径 | 说明 | 用途 |
|------|------|------|------|
| POST | `/reaction/record` | 保存反应力训练记录 | TeachReact.vue 训练结束后保存成绩 |
| GET | `/reaction/records` | 获取用户训练记录 | 查看历史训练成绩 |
| GET | `/reaction/statistics` | 获取训练统计信息 | 显示训练统计 |

---

## 六、线下课程管理 API (需新增)
### 基础路径: `/api/v1/offline-courses`

| 方法 | 路径 | 说明 | 用途 |
|------|------|------|------|
| GET | `/` | 获取线下课程列表（支持搜索、筛选） | Offline.vue 显示课程列表 |
| GET | `/{course_id}` | 获取线下课程详情 | Offline.vue 显示课程详情 |
| POST | `/{course_id}/enroll` | 报名线下课程 | Offline.vue 立即报名功能 |
| GET | `/my-enrollments` | 获取我的报名列表 | 查看已报名的课程 |

---

## 七、统计数据说明

### 学习统计 (`/api/v1/courses/statistics`)
返回数据包括：
- `total_study_time`: 总学习时长（分钟）
- `completed_courses`: 完成课程数
- `studying_courses`: 学习中课程数
- `favorite_courses`: 收藏课程数
- `skill_progress`: 技能进度列表

---

## 八、需要前端修改的硬编码部分

1. **首页 (Home.vue)**
   - ✅ 推荐课程已接入API（但有硬编码默认数据）
   - ❌ Banner数据硬编码
   - 需要：接入Banner API

2. **规则学习页 (TeachRule.vue)**
   - ❌ 规则内容硬编码
   - ❌ 学习进度使用本地存储
   - 需要：接入规则内容API和学习进度API

3. **反应力训练 (TeachReact.vue)**
   - ❌ 训练结果未保存到后端
   - 需要：接入训练记录API

4. **线下课程 (Offline.vue)**
   - ❌ 课程列表完全硬编码
   - ❌ 报名功能仅前端提示
   - 需要：接入线下课程API和报名API

5. **视频课程 (TeachVideo.vue)**
   - ❌ 部分硬编码，需要从courseId获取详情
   - ✅ 加入学习计划已部分接入API

---

## 九、API响应格式统一

### 成功响应
```json
{
  "id": 1,
  "title": "...",
  ...
}
```

### 列表响应
```json
{
  "total": 10,
  "items": [...]
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

---

## 十、认证说明

- 所有带 `🔒` 标记的接口需要JWT Token认证
- Token格式：`Authorization: Bearer {token}`
- Token过期自动返回401，前端应跳转到登录页

