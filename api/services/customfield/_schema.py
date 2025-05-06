from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from libs.models.json_schema import SchemaEntityType


class JsonSchemaBase(BaseModel):
    """JSON Schema基础模型，包含共同字段"""

    name: str = Field(..., description="Schema名称")
    entity_type: SchemaEntityType = Field(..., description="适用的实体类型")
    schema_value: Dict[str, Any] = Field(..., description="JSON Schema定义")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI展示相关的配置")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")

    @field_validator("schema_value")
    def validate_schema_value(cls, v):
        """验证JSON Schema格式"""
        # 简单验证，确保包含基本properties字段
        if not isinstance(v, dict) or "properties" not in v:
            raise ValueError("Schema必须是一个包含properties字段的JSON对象")
        return v


class JsonSchemaCreate(JsonSchemaBase):
    """创建JSON Schema的请求模型"""

    company_id: Optional[int] = Field(None, description="所属公司ID")
    is_system: bool = Field(False, description="是否为系统预设Schema")


class JsonSchemaUpdate(BaseModel):
    """更新JSON Schema的请求模型"""

    name: Optional[str] = Field(None, description="Schema名称")
    schema_value: Optional[Dict[str, Any]] = Field(None, description="JSON Schema定义")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI展示相关的配置")
    remark: Optional[str] = Field(None, max_length=255, description="备注信息")

    @field_validator("schema_value")
    def validate_schema_value(cls, v):
        """验证JSON Schema格式"""
        if v is not None:
            if not isinstance(v, dict) or "properties" not in v:
                raise ValueError("Schema必须是一个包含properties字段的JSON对象")
        return v


class JsonSchemaClone(BaseModel):
    """克隆JSON Schema的请求模型"""

    source_schema_id: int = Field(..., description="源Schema ID")
    target_company_id: int = Field(..., description="目标公司ID")
    name: Optional[str] = Field(None, description="新Schema名称，默认使用源Schema名称")


class JsonValueBase(BaseModel):
    """JSON值基础模型"""

    schema_id: int = Field(..., description="关联的JSON Schema ID")
    value: Dict[str, Any] = Field(..., description="JSON格式的数据值")
    remark: Optional[str] = Field(None, description="备注信息")


class JsonValueCreate(JsonValueBase):
    """创建JSON值的请求模型"""

    entity_id: int = Field(..., description="关联的实体ID")
    entity_type: str = Field(..., description="关联的实体类型")


class JsonValueUpdate(BaseModel):
    """更新JSON值的请求模型"""

    value: Dict[str, Any] = Field(..., description="JSON格式的数据值")
    remark: Optional[str] = Field(None, description="备注信息")


class JsonValueQuery(BaseModel):
    """查询JSON值的请求模型"""

    schema_id: Optional[int] = Field(None, description="关联的JSON Schema ID")
    entity_type: str = Field(..., description="关联的实体类型")
    entity_ids: List[int] = Field(..., description="关联的实体ID列表")


class JsonSchemaSchema(JsonSchemaBase):
    """JSON Schema响应模型"""

    id: int = Field(..., description="Schema ID")
    company_id: Optional[int] = Field(None, description="所属公司ID")
    is_system: bool = Field(..., description="是否为系统预设Schema")
    version: int = Field(..., description="Schema版本号")
    parent_schema_id: Optional[int] = Field(None, description="父Schema ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class JsonValueSchema(JsonValueBase):
    """JSON值响应模型"""

    id: int = Field(..., description="值ID")
    entity_id: int = Field(..., description="关联的实体ID")
    entity_type: str = Field(..., description="关联的实体类型")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class EntityWithCustomFieldSchema(BaseModel):
    """带有自定义字段的实体响应模型"""

    id: int = Field(..., description="实体ID")
    custom_fields: Dict[str, Union[JsonValueSchema, Dict[str, Any]]] = Field(
        default_factory=dict, description="自定义字段数据，键为schema_id或schema名称"
    )
