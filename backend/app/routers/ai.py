"""
AI教练相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.ai_chat import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.ai import (
    ChatRequest, ChatResponse,
    ActionAnalysisRequest,
    QuickQuestionRequest, QuickAnswerResponse,
    SessionListResponse, SessionResponse, SessionDetailResponse,
    ChatMessageResponse,
    PresetQuestion, PresetQuestionsResponse
)
from app.services.ai import chat_with_ai, simple_chat
from app.services.prompts import (
    VOLLEYBALL_COACH_SYSTEM,
    AI_ASSISTANT_SYSTEM,
    get_action_analysis_prompt,
    get_qa_prompt,
    PromptBuilder
)
from app.utils.security import get_current_user_optional


router = APIRouter(prefix="/ai", tags=["AI教练"])


# ========== 预设问题 ==========
PRESET_QUESTIONS = [
    PresetQuestion(id=1, category="技术动作", question="发球时手臂应该怎么挥？", icon="🏐"),
    PresetQuestion(id=2, category="技术动作", question="扣球如何发力更有效？", icon="💪"),
    PresetQuestion(id=3, category="技术动作", question="垫球手型应该怎么摆？", icon="🤲"),
    PresetQuestion(id=4, category="技术动作", question="传球怎么控制方向？", icon="🎯"),
    PresetQuestion(id=5, category="规则", question="什么情况算持球犯规？", icon="📋"),
    PresetQuestion(id=6, category="规则", question="自由人有哪些限制？", icon="🧍"),
    PresetQuestion(id=7, category="战术", question="5-1配备和4-2配备有什么区别？", icon="📊"),
    PresetQuestion(id=8, category="训练", question="新手每天应该练习多长时间？", icon="⏰"),
]


def require_session_owner(session: ChatSession, current_user: Optional[User]) -> None:
    user_id = current_user.id if current_user else None
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此会话"
        )


@router.get("/preset-questions", response_model=PresetQuestionsResponse)
def get_preset_questions():
    """获取预设问题列表"""
    return PresetQuestionsResponse(questions=PRESET_QUESTIONS)


@router.post("/chat", response_model=ChatResponse)
def chat_with_coach(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    与AI教练对话
    支持多轮对话，会自动保存对话历史
    """
    user_id = current_user.id if current_user else None
    
    # 获取或创建会话
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        require_session_owner(session, current_user)
    else:
        # 创建新会话
        session = ChatSession(
            user_id=user_id,
            session_type=request.context_type,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 获取历史消息
    history_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # 构建消息列表
    messages = []
    
    # 添加系统提示词
    if request.context_type == "coach":
        messages.append({"role": "system", "content": VOLLEYBALL_COACH_SYSTEM})
    else:
        messages.append({"role": "system", "content": AI_ASSISTANT_SYSTEM})
    
    # 添加历史消息（最近10条）
    for msg in history_messages[-10:]:
        messages.append({"role": msg.role, "content": msg.content})
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": request.message})
    
    # 调用AI
    result = chat_with_ai(messages)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'AI服务暂时不可用')
        )
    
    ai_response = result['content']
    tokens_used = result.get('usage', {}).get('total_tokens', 0)
    
    # 保存用户消息
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
        tokens_used=0
    )
    db.add(user_message)
    
    # 保存AI回复
    ai_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=ai_response,
        tokens_used=tokens_used
    )
    db.add(ai_message)
    
    # 更新会话时间
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return ChatResponse(
        success=True,
        message="对话成功",
        session_id=session.id,
        ai_response=ai_response,
        tokens_used=tokens_used
    )


@router.post("/analyze-action", response_model=ChatResponse)
def analyze_action(
    request: ActionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    动作分析
    专门分析排球动作并给出改进建议
    """
    user_id = current_user.id if current_user else None
    
    # 生成分析提示词
    prompt = get_action_analysis_prompt(
        action_type=request.action_type,
        user_description=request.description
    )
    
    # 获取或创建会话
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        require_session_owner(session, current_user)
    else:
        session = ChatSession(
            user_id=user_id,
            session_type="analysis",
            title=f"{request.action_type}动作分析"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 调用AI（使用教练系统提示词）
    result = simple_chat(prompt, system_prompt=VOLLEYBALL_COACH_SYSTEM)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'AI服务暂时不可用')
        )
    
    ai_response = result['content']
    tokens_used = result.get('usage', {}).get('total_tokens', 0)
    
    # 保存消息
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=f"[{request.action_type}分析] {request.description}",
        tokens_used=0
    )
    db.add(user_message)
    
    ai_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=ai_response,
        tokens_used=tokens_used
    )
    db.add(ai_message)
    db.commit()
    
    return ChatResponse(
        success=True,
        message="分析完成",
        session_id=session.id,
        ai_response=ai_response,
        tokens_used=tokens_used
    )


@router.post("/quick-answer", response_model=QuickAnswerResponse)
def quick_answer(request: QuickQuestionRequest):
    """
    快速问答
    适合简单问题，不保存对话历史
    """
    prompt = get_qa_prompt(request.question)
    result = simple_chat(prompt, system_prompt=AI_ASSISTANT_SYSTEM)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'AI服务暂时不可用')
        )
    
    return QuickAnswerResponse(
        success=True,
        answer=result['content'],
        tokens_used=result.get('usage', {}).get('total_tokens', 0)
    )


@router.get("/sessions", response_model=SessionListResponse)
def get_chat_sessions(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    获取用户的对话会话列表
    """
    if not current_user:
        return SessionListResponse(sessions=[], total=0)
    
    # 查询会话列表
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    total = query.count()
    
    sessions = query.order_by(ChatSession.updated_at.desc()).offset(offset).limit(limit).all()
    
    # 获取每个会话的消息数量
    session_responses = []
    for s in sessions:
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        session_responses.append(SessionResponse(
            id=s.id,
            session_type=s.session_type,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=msg_count
        ))
    
    return SessionListResponse(sessions=session_responses, total=total)


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取会话详情（包含消息历史）
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    require_session_owner(session, current_user)
    
    # 获取消息列表
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    msg_count = len(messages)
    
    return SessionDetailResponse(
        session=SessionResponse(
            id=session.id,
            session_type=session.session_type,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=msg_count
        ),
        messages=[ChatMessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at
        ) for m in messages]
    )


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    删除对话会话
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权删除"
        )
    
    # 删除消息和会话
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    
    return {"message": "会话已删除"}

