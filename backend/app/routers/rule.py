"""
规则内容相关路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.rule import RuleContent, RuleProgress
from app.models.user import User
from app.schemas.rule import (
    RuleContentResponse, RuleContentListResponse,
    RuleProgressCreate, RuleProgressResponse
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/rules", tags=["规则"])


@router.get("/content", response_model=RuleContentListResponse)
def get_rule_content(db: Session = Depends(get_db)):
    """
    获取规则内容
    """
    rules = db.query(RuleContent).filter(
        RuleContent.is_active == True
    ).order_by(RuleContent.section_order, RuleContent.sort_order).all()
    
    return RuleContentListResponse(total=len(rules), sections=rules)


@router.post("/progress", response_model=RuleProgressResponse)
def save_rule_progress(
    progress_data: RuleProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存规则学习进度
    """
    # 检查是否已有进度记录
    query = db.query(RuleProgress).filter(RuleProgress.user_id == current_user.id)
    
    if progress_data.rule_content_id:
        query = query.filter(RuleProgress.rule_content_id == progress_data.rule_content_id)
    
    progress = query.first()
    
    if progress:
        # 更新现有进度
        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
    else:
        # 创建新进度
        progress = RuleProgress(
            user_id=current_user.id,
            rule_content_id=progress_data.rule_content_id,
            is_completed=True,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    
    return progress

