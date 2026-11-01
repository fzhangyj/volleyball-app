"""
课程模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SkillType(Base):
    """
    技能类型表模型
    """
    __tablename__ = "skill_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="技能名称")
    skill_type = Column(String(50), nullable=False, unique=True, comment="技能类型标识")
    icon = Column(String(50), nullable=True, comment="图标（emoji或icon名称）")
    description = Column(Text, nullable=True, comment="技能描述")
    intro = Column(Text, nullable=True, comment="技能详细介绍")
    focus_points = Column(Text, nullable=True, comment="核心关注点（JSON数组）")
    training_methods = Column(Text, nullable=True, comment="训练方法（JSON数组）")
    tips = Column(Text, nullable=True, comment="注意事项（JSON数组）")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class CourseCategory(Base):
    """
    课程分类表模型
    """
    __tablename__ = "course_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="分类名称")
    description = Column(Text, nullable=True, comment="分类描述")
    icon = Column(String(255), nullable=True, comment="分类图标")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    courses = relationship("Course", back_populates="category")


class Course(Base):
    """
    课程表模型
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="课程标题")
    description = Column(Text, nullable=True, comment="课程描述")
    content = Column(Text, nullable=True, comment="课程内容")
    cover_image = Column(String(500), nullable=True, comment="封面图片")
    video_url = Column(String(500), nullable=True, comment="视频URL")
    category_id = Column(Integer, ForeignKey("course_categories.id"), nullable=True, comment="分类ID")
    skill_type = Column(String(50), nullable=True, comment="技能类型（托球、垫球、扣球等）")
    difficulty = Column(Integer, default=1, comment="难度等级（1-5）")
    duration = Column(Integer, default=0, comment="时长（分钟）")
    view_count = Column(Integer, default=0, comment="观看次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    category = relationship("CourseCategory", back_populates="courses")
    user_courses = relationship("UserCourse", back_populates="course")
    learning_progresses = relationship("LearningProgress", back_populates="course")


class UserCourse(Base):
    """
    用户课程关联表（收藏、加入学习计划等）
    """
    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, comment="课程ID")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    is_studying = Column(Boolean, default=False, comment="是否在学习")
    added_at = Column(DateTime(timezone=True), server_default=func.now(), comment="添加时间")
    
    # 关联关系
    user = relationship("User", backref="user_courses")
    course = relationship("Course", back_populates="user_courses")


class LearningProgress(Base):
    """
    学习进度表模型
    """
    __tablename__ = "learning_progresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, comment="课程ID")
    skill_type = Column(String(50), nullable=True, comment="技能类型")
    progress = Column(Integer, default=0, comment="进度百分比（0-100）")
    last_study_time = Column(DateTime(timezone=True), server_default=func.now(), comment="最后学习时间")
    study_duration = Column(Integer, default=0, comment="学习时长（分钟）")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", backref="learning_progresses")
    course = relationship("Course", back_populates="learning_progresses")

