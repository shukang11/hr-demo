from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class SchemaBaseModel(BaseModel):
    @classmethod
    def convert_datetime_2_int(cls, obj) -> int:
        if isinstance(obj, datetime):
            return int(obj.timestamp() * 1000)
        return obj

    @classmethod
    def convert_int_2_datetime(cls, obj) -> datetime:
        if isinstance(obj, int):
            return datetime.fromtimestamp(obj / 1000)
        return obj

    """
    HR系统的基础模型。
    """

    def model_dump_json(self, **kwargs):
        # 自定义序列化方法，将 datetime 转换为 13 位数字时间戳
        def custom_encoder(obj):
            SchemaBaseModel.convert_datetime_2_int(obj)
            return obj

        return super().model_dump_json(**kwargs, default=custom_encoder)


class PagePayload(SchemaBaseModel):
    """
    分页查询的参数模型。

    属性：
    - page (int): 页码。
    - per_page (int): 每页的数量。
    """

    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(10, ge=1, le=100, description="每页的数量")


T = TypeVar("T")


class PageResponse(SchemaBaseModel, Generic[T]):
    """
    分页查询的返回模型。

    属性：
    - total (int): 总数。
    - page (int): 页码。
    - per_page (int): 每页的数量。
    - items (List[T]): 数据列表。
    """

    total_count: int = Field(..., description="总数")
    page_count: int = Field(..., description="页码")
    page_limit: int = Field(..., description="每页的数量")
    current_page: int = Field(..., description="当前页码")
    items: List[T] = Field(..., description="数据列表")
