"""
短信验证码模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class SmsCode(Base):
    """
    短信验证码表模型
    """
    __tablename__ = "sms_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), index=True, nullable=False, comment="手机号")
    code = Column(String(10), nullable=False, comment="验证码")
    is_used = Column(Boolean, default=False, comment="是否已使用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")


