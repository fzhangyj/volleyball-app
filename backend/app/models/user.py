"""
用户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    用户表模型
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=True, comment="用户名")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    hashed_password = Column(String(255), nullable=True, comment="加密后的密码")
    avatar = Column(String(500), nullable=True, comment="头像路径")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    # 密码重置相关字段
    reset_token = Column(String(255), nullable=True, comment="密码重置token")
    reset_token_expires = Column(DateTime(timezone=True), nullable=True, comment="重置token过期时间")

