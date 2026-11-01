"""
AI相关的Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ========== 请求模式 ==========

class ChatRequest(BaseModel):
    """AI对话请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[int] = Field(None, description="会话ID（如有则继续对话）")
    context_type: str = Field("coach", description="上下文类型：coach教练/qa问答/analysis分析")


class ActionAnalysisRequest(BaseModel):
    """动作分析请求"""
    action_type: str = Field(..., description="动作类型：发球/扣球/垫球/传球/拦网等")
    description: str = Field(..., min_length=1, max_length=1000, description="动作描述或问题")
    session_id: Optional[int] = Field(None, description="会话ID")


class QuickQuestionRequest(BaseModel):
    """快速提问请求"""
    question: str = Field(..., min_length=1, max_length=500, description="问题内容")


# ========== 响应模式 ==========

class ChatMessageResponse(BaseModel):
    """对话消息响应"""
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """AI对话响应"""
    success: bool
    message: str = ""
    session_id: int
    ai_response: str
    tokens_used: int = 0


class SessionResponse(BaseModel):
    """会话信息响应"""
    id: int
    session_type: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[SessionResponse]
    total: int


class SessionDetailResponse(BaseModel):
    """会话详情响应（包含消息历史）"""
    session: SessionResponse
    messages: List[ChatMessageResponse]


class QuickAnswerResponse(BaseModel):
    """快速问答响应"""
    success: bool
    answer: str
    tokens_used: int = 0


# ========== 预设问题 ==========

class PresetQuestion(BaseModel):
    """预设问题"""
    id: int
    category: str
    question: str
    icon: str = "❓"


class PresetQuestionsResponse(BaseModel):
    """预设问题列表响应"""
    questions: List[PresetQuestion]

