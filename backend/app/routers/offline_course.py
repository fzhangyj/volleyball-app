"""
线下课程相关路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.offline_course import OfflineCourse, OfflineCourseEnrollment
from app.models.user import User
from app.schemas.offline_course import (
    OfflineCourseResponse, OfflineCourseListResponse,
    EnrollmentCreate, EnrollmentResponse
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/offline-courses", tags=["线下课程"])


# ========== 固定路径必须在动态路径之前 ==========

@router.get("/my-enrollments/list", response_model=List[EnrollmentResponse])
def get_my_enrollments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的报名列表
    """
    enrollments = db.query(OfflineCourseEnrollment).filter(
        OfflineCourseEnrollment.user_id == current_user.id
    ).order_by(OfflineCourseEnrollment.enrolled_at.desc()).all()
    
    return enrollments


@router.get("/", response_model=OfflineCourseListResponse)
def get_offline_courses(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    location: Optional[str] = Query(None, description="地区筛选"),
    db: Session = Depends(get_db)
):
    """
    获取线下课程列表
    """
    query = db.query(OfflineCourse).filter(OfflineCourse.is_active == True)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                OfflineCourse.title.contains(search),
                OfflineCourse.description.contains(search),
                OfflineCourse.location.contains(search)
            )
        )
    
    # 地区筛选
    if location:
        query = query.filter(OfflineCourse.location.contains(location))
    
    # 获取总数
    total = query.count()
    
    # 排序并分页
    courses = query.order_by(
        OfflineCourse.sort_order.desc(), 
        OfflineCourse.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return OfflineCourseListResponse(total=total, courses=courses)


@router.get("/{course_id}", response_model=OfflineCourseResponse)
def get_offline_course(course_id: int, db: Session = Depends(get_db)):
    """
    获取线下课程详情
    """
    course = db.query(OfflineCourse).filter(
        OfflineCourse.id == course_id,
        OfflineCourse.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    return course


@router.post("/{course_id}/enroll", response_model=EnrollmentResponse)
def enroll_offline_course(
    course_id: int,
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    报名线下课程
    """
    # 检查课程是否存在
    course = db.query(OfflineCourse).filter(OfflineCourse.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 检查是否已报名
    existing_enrollment = db.query(OfflineCourseEnrollment).filter(
        OfflineCourseEnrollment.user_id == current_user.id,
        OfflineCourseEnrollment.course_id == course_id,
        OfflineCourseEnrollment.status != "cancelled"
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已报名此课程"
        )
    
    # 检查是否还有名额
    if course.current_participants >= course.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="课程已满员"
        )
    
    # 创建报名记录
    enrollment = OfflineCourseEnrollment(
        user_id=current_user.id,
        course_id=course_id,
        contact_phone=enrollment_data.contact_phone,
        remark=enrollment_data.remark,
        status="pending"
    )
    db.add(enrollment)
    
    # 更新课程参与人数
    course.current_participants += 1
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment

