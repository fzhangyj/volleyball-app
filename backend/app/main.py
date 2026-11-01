"""
FastAPI应用主入口
"""
import os
from dotenv import load_dotenv

# 加载.env文件（在导入其他模块之前）
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, course, banner, rule, training, offline_course, ai
from app.config import API_V1_PREFIX, CORS_ORIGINS, UPLOAD_DIR, SMS_ENABLED
from app.database import init_db, init_default_data
from app.utils.upload import ensure_upload_dirs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    if not SMS_ENABLED:
        print("短信服务已禁用：未配置 Aliyun 凭据")
    # 启动时初始化数据库
    init_db()
    # 初始化默认数据
    init_default_data()
    # 确保上传目录存在
    ensure_upload_dirs()
    print("数据库初始化完成")
    yield
    # 关闭时清理资源（如果需要）
    print("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="排球APP后端API",
    description="排球教学APP的后端接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # 从配置读取，生产环境设置 CORS_ORIGINS 环境变量
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(course.router, prefix=API_V1_PREFIX)
app.include_router(banner.router, prefix=API_V1_PREFIX)
app.include_router(rule.router, prefix=API_V1_PREFIX)
app.include_router(training.router, prefix=API_V1_PREFIX)
app.include_router(offline_course.router, prefix=API_V1_PREFIX)
app.include_router(ai.router, prefix=API_V1_PREFIX)

# 静态文件服务（用于提供上传的文件访问）
try:
    ensure_upload_dirs()
    app.mount(f"{API_V1_PREFIX}/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
except Exception as e:
    print(f"警告: 无法挂载静态文件服务: {e}")


@app.get("/")
def root():
    """
    根路径
    """
    return {"message": "排球APP后端API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """
    健康检查
    """
    return {"status": "ok"}

