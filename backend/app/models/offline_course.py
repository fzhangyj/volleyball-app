"""
线下课程模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class OfflineCourse(Base):
    """
    线下课程表模型
    """
    __tablename__ = "offline_courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="课程标题")
    description = Column(Text, nullable=True, comment="课程描述")
    location = Column(String(200), nullable=False, comment="地点")
    address = Column(String(500), nullable=True, comment="详细地址")
    price = Column(Float, nullable=False, comment="价格")
    image_url = Column(String(500), nullable=True, comment="封面图片")
    max_participants = Column(Integer, default=20, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前参与人数")
    schedule_type = Column(String(50), nullable=True, comment="时间类型（weekly, appointment等）")
    schedule_info = Column(String(500), nullable=True, comment="时间安排描述")
    instructor_name = Column(String(100), nullable=True, comment="教练姓名")
    instructor_phone = Column(String(20), nullable=True, comment="教练电话")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    enrollments = relationship("OfflineCourseEnrollment", back_populates="course")


class OfflineCourseEnrollment(Base):
    """
    线下课程报名表模型
    """
    __tablename__ = "offline_course_enrollments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    course_id = Column(Integer, ForeignKey("offline_courses.id"), nullable=False, comment="课程ID")
    status = Column(String(50), default="pending", comment="报名状态（pending, confirmed, cancelled）")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    remark = Column(Text, nullable=True, comment="备注")
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), comment="报名时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", backref="offline_course_enrollments")
    course = relationship("OfflineCourse", back_populates="enrollments")

