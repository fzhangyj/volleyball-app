"""
配置文件
"""
import os
from dotenv import load_dotenv

# Load the same file for direct utility imports as for the app entry point.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 数据库配置 - 从环境变量读取，提供默认值用于开发环境
# 优先使用环境变量DB_TYPE，如果未设置则默认使用SQLite（开发环境推荐）
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # 可选: "sqlite" 或 "mysql"

if DB_TYPE == "mysql":
    # MySQL配置
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "my_app")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
else:
    # SQLite配置（默认，无需额外服务）
    DB_NAME = os.getenv("DB_NAME", "volleyball_app.db")
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DB_NAME)
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# JWT密钥必须显式配置，避免重启失效或使用公开默认密钥。
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if len(SECRET_KEY) < 32:
    raise RuntimeError("请在 backend/.env 或环境变量中配置至少32个字符的固定 SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# 密码重置token过期时间（分钟）
RESET_TOKEN_EXPIRE_MINUTES = 30

# 应用配置
API_V1_PREFIX = "/api/v1"

# CORS 配置 - 从环境变量读取，默认允许所有（开发环境）
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# 阿里云短信平台配置（号码认证服务 DYPNS）
ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID", "").strip()
ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "").strip()
SMS_ENABLED = bool(ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET)
ALIYUN_SMS_ENDPOINT = "dypnsapi.aliyuncs.com"
ALIYUN_SMS_SIGN_NAME = os.getenv("ALIYUN_SMS_SIGN_NAME", "速通互联验证码").strip()

# 阿里云短信模板CODE
SMS_TEMPLATE_REGISTER = os.getenv("SMS_TEMPLATE_REGISTER", "100001").strip()  # 注册/登录
SMS_TEMPLATE_CHANGE_PHONE = os.getenv("SMS_TEMPLATE_CHANGE_PHONE", "100002").strip()  # 修改手机号
SMS_TEMPLATE_RESET_PASSWORD = os.getenv("SMS_TEMPLATE_RESET_PASSWORD", "100003").strip()  # 修改密码
SMS_TEMPLATE_BIND_PHONE = os.getenv("SMS_TEMPLATE_BIND_PHONE", "100004").strip()  # 绑定新手机号
SMS_TEMPLATE_VERIFY_PHONE = os.getenv("SMS_TEMPLATE_VERIFY_PHONE", "100005").strip()  # 验证绑定手机号

# 验证码配置
SMS_CODE_EXPIRE_MINUTES = 5  # 验证码有效期（分钟）
SMS_CODE_LENGTH = 6  # 验证码长度
SMS_CODE_INTERVAL_SECONDS = 60  # 发送间隔（秒）

# 文件上传配置
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")  # 上传文件目录
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")  # 头像目录
MAX_FILE_SIZE = 5 * 1024 * 1024  # 最大文件大小 5MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/webp"]  # 允许的图片类型

# 火山方舟AI配置
VOLC_API_KEY = os.getenv("VOLC_API_KEY", "")
VOLC_API_BASE_URL = os.getenv("VOLC_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
VOLC_MODEL = os.getenv("VOLC_MODEL", "doubao-seed-1-8-251228")
VOLC_MAX_TOKENS = int(os.getenv("VOLC_MAX_TOKENS", "2000"))  # 最大返回token数
VOLC_TEMPERATURE = float(os.getenv("VOLC_TEMPERATURE", "0.7"))  # 温度参数 0-1
VOLC_TIMEOUT = int(os.getenv("VOLC_TIMEOUT", "30"))  # 请求超时时间（秒）

