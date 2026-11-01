# 排球APP后端

基于FastAPI开发的后端API服务。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

先复制 `.env.example` 为 `.env`（已有文件请保留），设置至少32个字符的固定 `SECRET_KEY`。可以运行 `py -c "import secrets; print(secrets.token_urlsafe(48))"` 生成一次并保存；重启或部署时使用同一值。未配置或过短会明确拒绝启动，避免生成临时密钥使登录失效。

短信需要同时配置 `ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET`，并使用账户中通过审核的签名和验证码模板。未配置凭据时短信发送和校验均不可用；登录必须通过阿里云验证码校验。AI 需要单独配置 `VOLC_API_KEY`。

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 本地冒烟检查

在本目录运行 `py smoke_test.py`。使用临时 SQLite 数据库和临时上传目录，不修改已有 `.env`、数据库或头像。覆盖注册/登录、短信发送及错误验证码拒绝、改名后继续认证、头像上传读取、课程收藏/进度、规则、三个训练模式、线下报名、AI 会话及固定 JWT 跨进程验证。短信 SDK 客户端和 AI 回复使用替身，不调用外部服务；实际短信送达和 AI 生成需另行验证。

运行 `py -m unittest test_sms -v` 可单独检查短信 SDK 请求与响应处理，包括 HTTP 200 但业务码为 `UNKNOWN` 时拒绝发送成功或登录。

## API接口

### 认证相关（/api/v1/auth）

- POST `/api/v1/auth/register` - 用户注册
- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/forgot-password` - 忘记密码
- POST `/api/v1/auth/reset-password` - 重置密码
- GET `/api/v1/auth/me` - 获取当前用户信息（需要token）

## 数据库

- MySQL地址：127.0.0.1:3306
- 用户名：root
- 密码：<SET_IN_ENV>
- 数据库名：my_app

启动时会自动创建数据库和表，无需手动执行SQL。

