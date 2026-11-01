"""
认证工具：获取当前用户
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

security = HTTPBearer()


def resolve_token_user(payload: dict, db: Session):
    """Use immutable IDs for new tokens; keep existing username/phone tokens valid."""
    sub = payload.get("sub")
    token_type = payload.get("type", "username")
    if sub is None:
        return None
    if token_type == "user_id":
        try:
            user_id = int(sub)
        except (ValueError, TypeError):
            return None
        user = db.query(User).filter(User.id == user_id).first()
    elif token_type == "phone":
        user = db.query(User).filter(User.phone == sub).first()
    else:
        user = db.query(User).filter(User.username == sub).first()
    return user if user and user.is_active else None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    支持用户名登录和手机号登录两种方式的token
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    sub: str = payload.get("sub")
    token_type: str = payload.get("type", "username")  # 默认为用户名登录
    
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = resolve_token_user(payload, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

