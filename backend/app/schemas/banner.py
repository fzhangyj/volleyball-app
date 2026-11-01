"""
Banner相关的Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BannerBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="标题")
    image_url: str = Field(..., max_length=500, description="图片URL")
    link_url: Optional[str] = Field(None, max_length=500, description="链接URL")
    link_type: Optional[str] = Field(None, max_length=50, description="链接类型")
    sort_order: int = Field(0, description="排序顺序")
    is_active: bool = Field(True, description="是否启用")


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    link_type: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class BannerResponse(BannerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

