"""
线下课程相关的Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OfflineCourseBase(BaseModel):
    title: str = Field(..., max_length=200, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    location: str = Field(..., max_length=200, description="地点")
    address: Optional[str] = Field(None, max_length=500, description="详细地址")
    price: float = Field(..., ge=0, description="价格")
    image_url: Optional[str] = Field(None, max_length=500, description="封面图片")
    max_participants: int = Field(20, ge=1, description="最大参与人数")
    schedule_type: Optional[str] = Field(None, max_length=50, description="时间类型")
    schedule_info: Optional[str] = Field(None, max_length=500, description="时间安排描述")
    instructor_name: Optional[str] = Field(None, max_length=100, description="教练姓名")
    instructor_phone: Optional[str] = Field(None, max_length=20, description="教练电话")
    sort_order: int = Field(0, description="排序顺序")


class OfflineCourseCreate(OfflineCourseBase):
    pass


class OfflineCourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    max_participants: Optional[int] = Field(None, ge=1)
    schedule_type: Optional[str] = Field(None, max_length=50)
    schedule_info: Optional[str] = Field(None, max_length=500)
    instructor_name: Optional[str] = Field(None, max_length=100)
    instructor_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class OfflineCourseResponse(OfflineCourseBase):
    id: int
    current_participants: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OfflineCourseListResponse(BaseModel):
    total: int
    courses: List[OfflineCourseResponse]


class EnrollmentCreate(BaseModel):
    course_id: int = Field(..., description="课程ID")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    remark: Optional[str] = Field(None, description="备注")


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    contact_phone: Optional[str]
    remark: Optional[str]
    enrolled_at: datetime
    course: Optional[OfflineCourseResponse] = None
    
    class Config:
        from_attributes = True

