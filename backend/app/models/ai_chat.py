"""
AI对话历史模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class MessageRole(str, enum.Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(Base):
    """
    AI对话会话表
    """
    __tablename__ = "ai_chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID（可为空，支持游客）")
    session_type = Column(String(50), default="coach", comment="会话类型：coach教练/qa问答/analysis分析")
    title = Column(String(200), nullable=True, comment="会话标题（取首条消息摘要）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ChatMessage(Base):
    """
    AI对话消息表
    """
    __tablename__ = "ai_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False, comment="会话ID")
    role = Column(String(20), nullable=False, comment="消息角色：user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    tokens_used = Column(Integer, default=0, comment="消耗的token数")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

