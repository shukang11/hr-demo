from typing import List, TypeVar, Any

from pydantic import BaseModel, Field, computed_field


T = TypeVar("T")

class PageRequest(BaseModel):
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页大小")

    @staticmethod
    def max_page() -> "PageRequest":
        return PageRequest(page=1, page_size=10000)

    @staticmethod
    def single_page(size: int) -> "PageRequest":
        return PageRequest(page=1, page_size=size)


class PageResponse(BaseModel):
    total_page: int = Field(..., description="总页数")
    cur_page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    data: List[Any] = Field(..., description="数据列表")
    
    # 为前端兼容添加的计算属性
    @computed_field
    def items(self) -> List[Any]:
        """兼容前端的items字段"""
        return self.data
        
    @computed_field
    def total(self) -> int:
        """总条数，根据页数和每页大小估算"""
        return (self.total_page - 1) * self.page_size + len(self.data)
        
    @computed_field
    def page(self) -> int:
        """兼容前端的page字段"""
        return self.cur_page
        
    @computed_field
    def limit(self) -> int:
        """兼容前端的limit字段"""
        return self.page_size

    @staticmethod
    def new(
        total_page: int, cur_page: int, page_size: int, data: List[T]
    ) -> "PageResponse":
        return PageResponse(
            total_page=total_page, cur_page=cur_page, page_size=page_size, data=data
        )