from typing import Optional

from pydantic import BaseModel, Field
from typing import Union, List


# 定义作者模型
class AuthorSchema(BaseModel):
    name: Optional[str] = Field(default=None)  # 作者姓名
    email: Optional[str] = Field(default=None)  # 作者邮箱
    uri: Optional[str] = Field(default=None)  # 作者URI


# 定义图片模型
class ImageSchema(BaseModel):
    url: Optional[str] = Field(default=None)  # 图片URL
    title: Optional[str] = Field(default=None)  # 图片标题
    width: Optional[int] = Field(default=None)  # 图片宽度
    height: Optional[int] = Field(default=None)  # 图片高度
    description: Optional[str] = Field(default=None)  # 图片描述


class IDPayload(BaseModel):
    ids: Union[int, List[int]] = Field(..., description="ID")

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure id is always a list for consistent handling
        if isinstance(self.ids, int):
            self.ids = [self.ids]


class IdentifierPayload(BaseModel):
    identifiers: Union[str, List[str]] = Field(..., description="Identifier")

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure identifier is always a list for consistent handling
        if isinstance(self.identifiers, str):
            self.identifiers = [self.identifiers]
