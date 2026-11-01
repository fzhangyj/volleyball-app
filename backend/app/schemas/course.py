"""
课程相关的Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CourseCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, description="分类图标")
    sort_order: int = Field(0, description="排序顺序")


class CourseCategoryCreate(CourseCategoryBase):
    pass


class CourseCategoryResponse(CourseCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    title: str = Field(..., max_length=200, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    content: Optional[str] = Field(None, description="课程内容")
    cover_image: Optional[str] = Field(None, description="封面图片")
    video_url: Optional[str] = Field(None, description="视频URL")
    category_id: Optional[int] = Field(None, description="分类ID")
    skill_type: Optional[str] = Field(None, description="技能类型")
    difficulty: int = Field(1, ge=1, le=5, description="难度等级（1-5）")
    duration: int = Field(0, description="时长（分钟）")
    sort_order: int = Field(0, description="排序顺序")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    content: Optional[str] = Field(None, description="课程内容")
    cover_image: Optional[str] = Field(None, description="封面图片")
    video_url: Optional[str] = Field(None, description="视频URL")
    category_id: Optional[int] = Field(None, description="分类ID")
    skill_type: Optional[str] = Field(None, description="技能类型")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度等级（1-5）")
    duration: Optional[int] = Field(None, description="时长（分钟）")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort_order: Optional[int] = Field(None, description="排序顺序")


class CourseResponse(CourseBase):
    id: int
    view_count: int
    like_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CourseCategoryResponse] = None
    
    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    total: int
    courses: List[CourseResponse]


class UserCourseCreate(BaseModel):
    course_id: int = Field(..., description="课程ID")
    is_favorite: bool = Field(False, description="是否收藏")
    is_studying: bool = Field(False, description="是否在学习")


class UserCourseResponse(BaseModel):
    id: int
    course_id: int
    is_favorite: bool
    is_studying: bool
    added_at: datetime
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True


class LearningProgressCreate(BaseModel):
    course_id: Optional[int] = Field(None, description="课程ID")
    skill_type: Optional[str] = Field(None, description="技能类型")
    progress: int = Field(0, ge=0, le=100, description="进度百分比（0-100）")
    study_duration: int = Field(0, description="学习时长（分钟）")


class LearningProgressUpdate(BaseModel):
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度百分比（0-100）")
    study_duration: Optional[int] = Field(None, description="学习时长（分钟）")
    completed: Optional[bool] = Field(None, description="是否完成")


class LearningProgressResponse(BaseModel):
    id: int
    course_id: Optional[int]
    skill_type: Optional[str]
    progress: int
    study_duration: int
    last_study_time: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True


class LearningStatisticsResponse(BaseModel):
    total_study_time: int = Field(0, description="总学习时长（分钟）")
    completed_courses: int = Field(0, description="完成课程数")
    studying_courses: int = Field(0, description="学习中课程数")
    favorite_courses: int = Field(0, description="收藏课程数")
    skill_progress: List[dict] = Field(default_factory=list, description="技能进度列表")

