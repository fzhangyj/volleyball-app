"""
Banner相关路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.banner import Banner
from app.schemas.banner import BannerResponse, BannerCreate, BannerUpdate

router = APIRouter(prefix="/banners", tags=["Banner"])


@router.get("/", response_model=List[BannerResponse])
def get_banners(db: Session = Depends(get_db)):
    """
    获取Banner列表（仅返回启用的）
    """
    banners = db.query(Banner).filter(
        Banner.is_active == True
    ).order_by(Banner.sort_order.desc(), Banner.created_at.desc()).all()
    
    return banners


@router.get("/{banner_id}", response_model=BannerResponse)
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    """
    获取Banner详情
    """
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    return banner

