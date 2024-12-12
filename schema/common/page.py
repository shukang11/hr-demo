from typing import List, TypeVar

from pydantic import BaseModel, Field


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
    data: List[T] = Field(..., description="数据列表")

    @staticmethod
    def new(
        total_page: int, cur_page: int, page_size: int, data: List[T]
    ) -> "PageResponse":
        return PageResponse(
            total_page=total_page, cur_page=cur_page, page_size=page_size, data=data
        )