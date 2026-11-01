"""
规则内容相关的Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RuleContentBase(BaseModel):
    title: str = Field(..., max_length=200, description="标题")
    content: str = Field(..., description="内容")
    section_title: Optional[str] = Field(None, max_length=200, description="章节标题")
    section_order: int = Field(0, description="章节排序")
    image_url: Optional[str] = Field(None, max_length=500, description="配图URL")
    sort_order: int = Field(0, description="排序顺序")


class RuleContentResponse(RuleContentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RuleContentListResponse(BaseModel):
    total: int
    sections: List[RuleContentResponse]


class RuleProgressCreate(BaseModel):
    rule_content_id: Optional[int] = Field(None, description="规则内容ID（可选，如果为空表示完成所有规则）")


class RuleProgressResponse(BaseModel):
    id: int
    user_id: int
    rule_content_id: Optional[int]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

