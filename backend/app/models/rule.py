"""
规则内容模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class RuleContent(Base):
    """
    规则内容表模型
    """
    __tablename__ = "rule_contents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    section_title = Column(String(200), nullable=True, comment="章节标题")
    section_order = Column(Integer, default=0, comment="章节排序")
    image_url = Column(String(500), nullable=True, comment="配图URL")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")


class RuleProgress(Base):
    """
    规则学习进度表模型
    """
    __tablename__ = "rule_progresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    rule_content_id = Column(Integer, ForeignKey("rule_contents.id"), nullable=True, comment="规则内容ID")
    is_completed = Column(Boolean, default=False, comment="是否完成")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", backref="rule_progresses")
    rule_content = relationship("RuleContent", backref="rule_progresses")

