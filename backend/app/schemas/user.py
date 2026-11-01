"""
用户相关的Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """注册请求模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """登录请求模式"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模式"""
    id: int
    username: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户资料更新模式"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")


class Token(BaseModel):
    """Token响应模式"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordReset(BaseModel):
    """忘记密码请求模式"""
    username: str = Field(..., description="用户名")


class PasswordResetConfirm(BaseModel):
    """重置密码确认模式"""
    username: str = Field(..., description="用户名")
    token: str = Field(..., description="重置token")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


# ========== 短信验证码相关 ==========

class SendSmsCodeRequest(BaseModel):
    """发送短信验证码请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    scene: Optional[str] = Field(default="register", description="场景：register, reset_password等")


class SendSmsCodeResponse(BaseModel):
    """发送短信验证码响应"""
    success: bool
    message: str


class SmsLoginRequest(BaseModel):
    """短信验证码登录请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    code: str = Field(..., min_length=4, max_length=8, description="验证码")


class UserRegisterWithSms(BaseModel):
    """带短信验证码的注册请求"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    sms_code: str = Field(..., min_length=6, max_length=6, description="短信验证码")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名（可选，默认为手机号后4位）")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class PasswordResetWithSms(BaseModel):
    """使用短信验证码重置密码"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    sms_code: str = Field(..., min_length=6, max_length=6, description="短信验证码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

