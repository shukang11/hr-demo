from typing import Optional
from pydantic import BaseModel, Field


class PositionBase(BaseModel):
    name: str = Field(..., max_length=64, description="职位名称")
    company_id: int = Field(..., description="所属公司ID")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64, description="职位名称")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")


class PositionSchema(PositionBase):
    id: int = Field(..., description="职位ID")

    class Config:
        from_attributes = True
