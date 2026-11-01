"""
文件上传工具
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import UPLOAD_DIR, AVATAR_DIR, MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES


def ensure_upload_dirs():
    """
    确保上传目录存在
    """
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(AVATAR_DIR).mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    验证图片文件
    """
    # 检查文件类型
    if file.content_type and file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 如果没有content_type，尝试从文件名判断
    if not file.content_type and file.filename:
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型，仅支持: {', '.join(allowed_exts)}"
            )


def save_avatar_file(file: UploadFile, user_id: int) -> str:
    """
    保存头像文件
    返回相对路径（用于数据库存储）
    """
    ensure_upload_dirs()
    
    # 验证文件
    validate_image_file(file)
    
    # 生成唯一文件名
    file_ext = Path(file.filename).suffix if file.filename else ".jpg"
    if not file_ext or file_ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        file_ext = ".jpg"
    
    filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = Path(AVATAR_DIR) / filename
    
    # 读取文件内容
    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"读取文件失败: {str(e)}"
        )
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE / 1024 / 1024}MB）"
        )
    
    # 检查文件是否为空
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件为空"
        )
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存文件失败: {str(e)}"
        )
    
    # 返回相对路径（相对于uploads目录）
    relative_path = f"avatars/{filename}"
    return relative_path


def delete_avatar_file(avatar_path: str) -> None:
    """
    删除头像文件
    """
    if not avatar_path:
        return
    
    # avatar_path是相对路径，需要转换为绝对路径
    file_path = Path(UPLOAD_DIR) / avatar_path
    
    # 如果文件存在，删除它
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"删除头像文件失败: {e}")


def get_avatar_url(avatar_path: str) -> str:
    """
    获取头像URL（用于返回给前端）
    """
    if not avatar_path:
        return ""
    
    # 返回相对路径，前端可以通过 /api/v1/uploads/ 访问
    return f"/api/v1/uploads/{avatar_path}"

