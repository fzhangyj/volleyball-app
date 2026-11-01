"""
训练记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ReactionTrainingRecord(Base):
    """
    反应力训练记录表模型
    """
    __tablename__ = "reaction_training_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    game_mode = Column(String(50), nullable=False, comment="游戏模式（ball, color, direction）")
    score = Column(Integer, default=0, comment="得分")
    avg_reaction_time = Column(Float, nullable=True, comment="平均反应时间（毫秒）")
    hit_rate = Column(Float, nullable=True, comment="命中率（百分比）")
    total_rounds = Column(Integer, default=0, comment="总回合数")
    hit_count = Column(Integer, default=0, comment="命中次数")
    duration = Column(Integer, default=0, comment="训练时长（秒）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    user = relationship("User", backref="reaction_training_records")

