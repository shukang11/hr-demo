from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from libs.models.candidate import CandidateStatus


class CandidateBase(BaseModel):
    """候选人基础模型，包含共同字段"""
    company_id: int = Field(..., description="公司ID")
    name: str = Field(..., max_length=64, description="候选人姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=255, description="电子邮箱")
    position_id: int = Field(..., description="应聘职位ID")
    department_id: int = Field(..., description="目标部门ID")
    interview_date: Optional[datetime] = Field(None, description="面试日期")
    interviewer_id: Optional[int] = Field(None, description="面试官ID")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")


class CandidateCreate(CandidateBase):
    """创建候选人的请求模型"""
    status: CandidateStatus = Field(default=CandidateStatus.PENDING, description="候选人状态")


class CandidateUpdate(BaseModel):
    """更新候选人的请求模型，所有字段可选"""
    name: Optional[str] = Field(None, max_length=64, description="候选人姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=255, description="电子邮箱")
    position_id: Optional[int] = Field(None, description="应聘职位ID")
    department_id: Optional[int] = Field(None, description="目标部门ID")
    interview_date: Optional[datetime] = Field(None, description="面试日期")
    interviewer_id: Optional[int] = Field(None, description="面试官ID")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")
    extra_value: Optional[Dict[str, Any]] = Field(None, description="附加JSON格式数据")
    extra_schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")


class CandidateStatusUpdate(BaseModel):
    """更新候选人状态的请求模型"""
    status: CandidateStatus = Field(..., description="候选人状态")
    evaluation: Optional[str] = Field(None, description="面试评价")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")


class CandidateSchema(CandidateBase):
    """候选人响应模型，用于API返回"""
    id: int = Field(..., description="候选人ID")
    status: CandidateStatus = Field(..., description="候选人状态")
    evaluation: Optional[str] = Field(None, description="面试评价")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True