"""
训练记录相关的Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReactionTrainingRecordCreate(BaseModel):
    game_mode: str = Field(..., description="游戏模式（ball, color, direction）")
    score: int = Field(0, description="得分")
    avg_reaction_time: Optional[float] = Field(None, description="平均反应时间（毫秒）")
    hit_rate: Optional[float] = Field(None, description="命中率（百分比）")
    total_rounds: int = Field(0, description="总回合数")
    hit_count: int = Field(0, description="命中次数")
    duration: int = Field(0, description="训练时长（秒）")


class ReactionTrainingRecordResponse(BaseModel):
    id: int
    user_id: int
    game_mode: str
    score: int
    avg_reaction_time: Optional[float]
    hit_rate: Optional[float]
    total_rounds: int
    hit_count: int
    duration: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReactionTrainingStatisticsResponse(BaseModel):
    total_records: int = Field(0, description="总记录数")
    best_score: int = Field(0, description="最高分")
    best_avg_reaction_time: Optional[float] = Field(None, description="最佳平均反应时间")
    total_duration: int = Field(0, description="总训练时长（秒）")
    mode_stats: List[dict] = Field(default_factory=list, description="各模式统计")

