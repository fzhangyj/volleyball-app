"""
Banner模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Banner(Base):
    """
    Banner轮播图表模型
    """
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=True, comment="标题")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    link_url = Column(String(500), nullable=True, comment="链接URL")
    link_type = Column(String(50), nullable=True, comment="链接类型（course, page等）")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

