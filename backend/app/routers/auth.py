"""
认证相关路由：注册、登录、忘记密码、短信验证码登录
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.sms_code import SmsCode
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, UserUpdate,
    PasswordReset, PasswordResetConfirm,
    SendSmsCodeRequest, SendSmsCodeResponse, SmsLoginRequest,
    UserRegisterWithSms, PasswordResetWithSms
)
from fastapi import UploadFile, File
from app.utils.upload import save_avatar_file, delete_avatar_file, get_avatar_url
from app.utils.security import verify_password, get_password_hash, create_access_token, generate_reset_token
from app.utils.sms import send_sms, validate_phone, check_sms_code
from app.utils.auth import get_current_user
from app.config import RESET_TOKEN_EXPIRE_MINUTES, SMS_CODE_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册（用户名+密码方式）
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/register-with-sms", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_with_sms(user_data: UserRegisterWithSms, db: Session = Depends(get_db)):
    """
    用户注册（手机号+短信验证码方式）
    """
    phone = user_data.phone
    sms_code = user_data.sms_code
    
    # 验证手机号格式
    if not validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 检查手机号是否已注册
    existing_user = db.query(User).filter(User.phone == phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )
    
    # 校验短信验证码（调用阿里云接口）
    is_valid, message = check_sms_code(phone, sms_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 检查用户名是否已存在（如果提供了用户名）
    username = user_data.username or f"用户{phone[-4:]}"
    if user_data.username:
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=username,
        phone=phone,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    """
    # 查找用户
    db_user = db.query(User).filter(User.username == login_data.username).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(login_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户是否激活
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 生成token
    access_token = create_access_token(data={"sub": str(db_user.id), "type": "user_id"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/forgot-password")
def forgot_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    忘记密码：生成重置密码token
    """
    # 查找用户
    db_user = db.query(User).filter(User.username == reset_data.username).first()
    
    if not db_user:
        # 为了安全，即使用户不存在也返回成功（防止用户枚举攻击）
        return {"message": "如果该用户已注册，重置验证码已生成"}
    
    # 生成重置token
    reset_token = generate_reset_token()
    
    # 设置token过期时间
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    
    # 保存到数据库
    db_user.reset_token = reset_token
    db_user.reset_token_expires = expires_at
    db.commit()
    
    # 返回token（测试用，生产环境应通过其他方式发送）
    return {
        "message": "如果该用户已注册，重置验证码已生成",
        "reset_token": reset_token,
        "expires_in_minutes": RESET_TOKEN_EXPIRE_MINUTES
    }


@router.post("/reset-password")
def reset_password(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    重置密码（需要有效的重置token）- 旧方式
    """
    # 查找用户
    db_user = db.query(User).filter(User.username == reset_data.username).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证重置token
    if not db_user.reset_token or db_user.reset_token != reset_data.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的重置验证码"
        )
    
    # 检查token是否过期
    if not db_user.reset_token_expires or db_user.reset_token_expires < datetime.utcnow():
        # 清除过期的token
        db_user.reset_token = None
        db_user.reset_token_expires = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置验证码已过期，请重新申请"
        )
    
    # 更新密码
    db_user.hashed_password = get_password_hash(reset_data.new_password)
    
    # 清除重置token（一次性使用）
    db_user.reset_token = None
    db_user.reset_token_expires = None
    db.commit()
    
    return {"message": "密码重置成功"}


@router.post("/reset-password-with-sms")
def reset_password_with_sms(reset_data: PasswordResetWithSms, db: Session = Depends(get_db)):
    """
    重置密码（使用短信验证码）- 推荐方式
    """
    phone = reset_data.phone
    sms_code = reset_data.sms_code
    
    # 验证手机号格式
    if not validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 查找用户
    db_user = db.query(User).filter(User.phone == phone).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该手机号未注册"
        )
    
    # 校验短信验证码（调用阿里云接口）
    is_valid, message = check_sms_code(phone, sms_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 更新密码
    db_user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()
    
    return {"message": "密码重置成功"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料
    """
    # 更新用户名
    if user_data.username is not None:
        # 检查用户名是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        current_user.username = user_data.username
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    """
    old_avatar_path = None
    try:
        # 记录旧头像路径（如果存在）
        if current_user.avatar:
            old_avatar_path = current_user.avatar
        
        # 保存新头像
        avatar_path = save_avatar_file(file, current_user.id)
        
        # 更新数据库
        current_user.avatar = avatar_path
        db.commit()
        db.refresh(current_user)
        
        # 如果新头像保存成功，删除旧头像
        if old_avatar_path and old_avatar_path != avatar_path:
            try:
                delete_avatar_file(old_avatar_path)
            except Exception as e:
                # 删除旧头像失败不影响主流程，只记录日志
                print(f"警告: 删除旧头像失败: {e}")
        
        # 返回用户信息（包含avatar字段）
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        # 如果保存失败，尝试回滚（删除可能已保存的新文件）
        if current_user.avatar and current_user.avatar != old_avatar_path:
            try:
                delete_avatar_file(current_user.avatar)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传头像失败: {str(e)}"
        )


# ========== 短信验证码登录相关接口 ==========

@router.post("/send-sms-code", response_model=SendSmsCodeResponse)
def send_sms_code(request: SendSmsCodeRequest, db: Session = Depends(get_db)):
    """
    发送短信验证码（使用阿里云DYPNS服务）
    支持的场景：register（注册/登录）、reset_password（重置密码）
    """
    phone = request.phone
    scene = getattr(request, 'scene', 'register')  # 默认场景为注册
    
    # 验证手机号格式
    if not validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 注意：移除了60秒频率限制，允许连续发送（阿里云自身有频率控制）
    
    # 调用阿里云发送短信（阿里云自动生成和管理验证码）
    result = send_sms(phone, scene)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['message']
        )
    
    # 记录发送历史（用于频率控制，不保存验证码本身）
    expires_at = datetime.utcnow() + timedelta(minutes=SMS_CODE_EXPIRE_MINUTES)
    sms_code = SmsCode(
        phone=phone,
        code="",  # 阿里云管理验证码，不在本地保存
        expires_at=expires_at,
        is_used=False
    )
    db.add(sms_code)
    db.commit()
    
    return SendSmsCodeResponse(
        success=True,
        message="验证码发送成功，有效期5分钟"
    )


@router.post("/sms-login", response_model=Token)
def sms_login(request: SmsLoginRequest, db: Session = Depends(get_db)):
    """
    短信验证码登录
    - 如果用户不存在，自动注册
    - 如果用户存在，直接登录
    """
    phone = request.phone
    code = request.code
    
    # 验证手机号格式
    if not validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 调用阿里云接口校验验证码
    is_valid, message = check_sms_code(phone, code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 查找或创建用户
    db_user = db.query(User).filter(User.phone == phone).first()
    
    if not db_user:
        # 自动注册新用户
        db_user = User(
            phone=phone,
            username=f"用户{phone[-4:]}",  # 默认用户名为"用户+手机后4位"
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # 检查用户是否激活
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 生成token（使用手机号作为标识）
    access_token = create_access_token(data={"sub": str(db_user.id), "type": "user_id"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

