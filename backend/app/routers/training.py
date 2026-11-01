"""
训练记录相关路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.training import ReactionTrainingRecord
from app.models.user import User
from app.schemas.training import (
    ReactionTrainingRecordCreate, ReactionTrainingRecordResponse,
    ReactionTrainingStatisticsResponse
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/training", tags=["训练"])


@router.post("/reaction/record", response_model=ReactionTrainingRecordResponse)
def save_reaction_training_record(
    record_data: ReactionTrainingRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存反应力训练记录
    """
    record = ReactionTrainingRecord(
        user_id=current_user.id,
        game_mode=record_data.game_mode,
        score=record_data.score,
        avg_reaction_time=record_data.avg_reaction_time,
        hit_rate=record_data.hit_rate,
        total_rounds=record_data.total_rounds,
        hit_count=record_data.hit_count,
        duration=record_data.duration
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record


@router.get("/reaction/records", response_model=List[ReactionTrainingRecordResponse])
def get_reaction_records(
    game_mode: Optional[str] = Query(None, description="游戏模式"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户训练记录
    """
    query = db.query(ReactionTrainingRecord).filter(
        ReactionTrainingRecord.user_id == current_user.id
    )
    
    if game_mode:
        query = query.filter(ReactionTrainingRecord.game_mode == game_mode)
    
    records = query.order_by(ReactionTrainingRecord.created_at.desc()).limit(limit).all()
    
    return records


@router.get("/reaction/statistics", response_model=ReactionTrainingStatisticsResponse)
def get_reaction_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取训练统计信息
    """
    # 总记录数
    total_records = db.query(func.count(ReactionTrainingRecord.id)).filter(
        ReactionTrainingRecord.user_id == current_user.id
    ).scalar() or 0
    
    # 最高分
    best_score = db.query(func.max(ReactionTrainingRecord.score)).filter(
        ReactionTrainingRecord.user_id == current_user.id
    ).scalar() or 0
    
    # 最佳平均反应时间
    best_avg_time = db.query(func.min(ReactionTrainingRecord.avg_reaction_time)).filter(
        ReactionTrainingRecord.user_id == current_user.id,
        ReactionTrainingRecord.avg_reaction_time.isnot(None)
    ).scalar()
    
    # 总训练时长
    total_duration = db.query(func.sum(ReactionTrainingRecord.duration)).filter(
        ReactionTrainingRecord.user_id == current_user.id
    ).scalar() or 0
    
    # 各模式统计
    mode_stats = []
    modes = ['ball', 'color', 'direction']
    for mode in modes:
        mode_records = db.query(ReactionTrainingRecord).filter(
            ReactionTrainingRecord.user_id == current_user.id,
            ReactionTrainingRecord.game_mode == mode
        ).all()
        
        if mode_records:
            mode_stats.append({
                "mode": mode,
                "count": len(mode_records),
                "best_score": max([r.score for r in mode_records]),
                "avg_score": sum([r.score for r in mode_records]) / len(mode_records) if mode_records else 0
            })
    
    return ReactionTrainingStatisticsResponse(
        total_records=total_records,
        best_score=int(best_score),
        best_avg_reaction_time=float(best_avg_time) if best_avg_time else None,
        total_duration=int(total_duration),
        mode_stats=mode_stats
    )

