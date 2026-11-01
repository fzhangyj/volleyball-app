"""
课程相关路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.course import Course, CourseCategory, UserCourse, LearningProgress, SkillType
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    UserCourseCreate, UserCourseResponse,
    LearningProgressCreate, LearningProgressUpdate, LearningProgressResponse,
    LearningStatisticsResponse
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["课程"])


@router.get("/", response_model=CourseListResponse)
def get_courses(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    skill_type: Optional[str] = Query(None, description="技能类型"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取课程列表
    """
    query = db.query(Course).filter(Course.is_active == True)
    
    # 分类筛选
    if category_id:
        query = query.filter(Course.category_id == category_id)
    
    # 技能类型筛选
    if skill_type:
        query = query.filter(Course.skill_type == skill_type)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                Course.title.contains(search),
                Course.description.contains(search)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 排序并分页
    courses = query.order_by(Course.sort_order.desc(), Course.created_at.desc()).offset(skip).limit(limit).all()
    
    return CourseListResponse(total=total, courses=courses)


# ========== 学习统计（必须在 /{course_id} 之前定义）==========

@router.get("/statistics", response_model=LearningStatisticsResponse)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学习统计信息
    """
    # 总学习时长
    total_study_time = db.query(func.sum(LearningProgress.study_duration)).filter(
        LearningProgress.user_id == current_user.id
    ).scalar() or 0
    
    # 完成课程数
    completed_courses = db.query(func.count(LearningProgress.id)).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.progress >= 100
    ).scalar() or 0
    
    # 学习中课程数
    studying_courses = db.query(func.count(UserCourse.id)).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.is_studying == True
    ).scalar() or 0
    
    # 收藏课程数
    favorite_courses = db.query(func.count(UserCourse.id)).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.is_favorite == True
    ).scalar() or 0
    
    # 技能进度列表
    skill_progresses = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.skill_type.isnot(None)
    ).all()
    
    skill_progress_list = [
        {
            "skill_type": p.skill_type,
            "progress": p.progress,
            "study_duration": p.study_duration
        }
        for p in skill_progresses
    ]
    
    return LearningStatisticsResponse(
        total_study_time=int(total_study_time),
        completed_courses=completed_courses,
        studying_courses=studying_courses,
        favorite_courses=favorite_courses,
        skill_progress=skill_progress_list
    )


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    获取课程详情
    """
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 增加观看次数
    course.view_count += 1
    db.commit()
    db.refresh(course)
    
    return course


@router.get("/categories/list", response_model=List[dict])
def get_categories(db: Session = Depends(get_db)):
    """
    获取课程分类列表
    """
    categories = db.query(CourseCategory).order_by(CourseCategory.sort_order).all()
    return [{"id": cat.id, "name": cat.name, "icon": cat.icon, "description": cat.description} for cat in categories]


@router.get("/skills/list", response_model=List[dict])
def get_skill_types(db: Session = Depends(get_db)):
    """
    获取技能类型列表
    """
    skills = db.query(SkillType).filter(SkillType.is_active == True).order_by(SkillType.sort_order).all()
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "skillType": skill.skill_type,
            "icon": skill.icon,
            "description": skill.description
        }
        for skill in skills
    ]


@router.get("/skills/{skill_type}/detail", response_model=dict)
def get_skill_detail(skill_type: str, db: Session = Depends(get_db)):
    """
    获取技能详情
    """
    import json
    skill = db.query(SkillType).filter(
        SkillType.skill_type == skill_type,
        SkillType.is_active == True
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能类型不存在"
        )
    
    # 解析JSON字段
    focus_points = []
    training_methods = []
    tips = []
    
    try:
        if skill.focus_points:
            focus_points = json.loads(skill.focus_points)
        if skill.training_methods:
            training_methods = json.loads(skill.training_methods)
        if skill.tips:
            tips = json.loads(skill.tips)
    except json.JSONDecodeError:
        pass
    
    return {
        "id": skill.id,
        "name": skill.name,
        "skillType": skill.skill_type,
        "icon": skill.icon,
        "description": skill.description,
        "intro": skill.intro,
        "focusPoints": focus_points,
        "trainingMethods": training_methods,
        "tips": tips
    }


# ========== 用户课程相关 ==========

@router.post("/favorites", response_model=UserCourseResponse)
def add_favorite(
    data: UserCourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    收藏课程
    """
    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 检查是否已收藏
    user_course = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.course_id == data.course_id
    ).first()
    
    if user_course:
        # 更新收藏状态
        user_course.is_favorite = data.is_favorite
        user_course.is_studying = data.is_studying
    else:
        # 创建新记录
        user_course = UserCourse(
            user_id=current_user.id,
            course_id=data.course_id,
            is_favorite=data.is_favorite,
            is_studying=data.is_studying
        )
        db.add(user_course)
    
    db.commit()
    db.refresh(user_course)
    
    return user_course


@router.get("/favorites/list", response_model=List[UserCourseResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取收藏的课程列表
    """
    user_courses = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.is_favorite == True
    ).order_by(UserCourse.added_at.desc()).all()
    
    return user_courses


@router.delete("/favorites/{course_id}")
def remove_favorite(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消收藏
    """
    user_course = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.course_id == course_id
    ).first()
    
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到收藏记录"
        )
    
    user_course.is_favorite = False
    if not user_course.is_studying:
        db.delete(user_course)
    
    db.commit()
    
    return {"message": "取消收藏成功"}


@router.get("/studying/list", response_model=List[UserCourseResponse])
def get_studying_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学习中的课程列表
    """
    user_courses = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.is_studying == True
    ).order_by(UserCourse.added_at.desc()).all()
    
    return user_courses


# ========== 学习进度相关 ==========

@router.post("/progress", response_model=LearningProgressResponse)
def create_progress(
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建或更新学习进度
    """
    # 查找现有进度
    progress_query = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    )
    
    if data.course_id:
        progress_query = progress_query.filter(LearningProgress.course_id == data.course_id)
    elif data.skill_type:
        progress_query = progress_query.filter(LearningProgress.skill_type == data.skill_type)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供course_id或skill_type"
        )
    
    progress = progress_query.first()
    
    if progress:
        # 更新现有进度
        progress.progress = data.progress
        progress.study_duration += data.study_duration
        if data.progress >= 100 and not progress.completed_at:
            from datetime import datetime, timezone
            progress.completed_at = datetime.now(timezone.utc)
    else:
        # 创建新进度
        progress = LearningProgress(
            user_id=current_user.id,
            course_id=data.course_id,
            skill_type=data.skill_type,
            progress=data.progress,
            study_duration=data.study_duration
        )
        if data.progress >= 100:
            from datetime import datetime, timezone
            progress.completed_at = datetime.now(timezone.utc)
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    
    return progress


@router.get("/progress/list", response_model=List[LearningProgressResponse])
def get_progress_list(
    skill_type: Optional[str] = Query(None, description="技能类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学习进度列表
    """
    query = db.query(LearningProgress).filter(LearningProgress.user_id == current_user.id)
    
    if skill_type:
        query = query.filter(LearningProgress.skill_type == skill_type)
    
    progresses = query.order_by(LearningProgress.last_study_time.desc()).all()
    
    return progresses

