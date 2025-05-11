from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field
from flask import jsonify, Response
from libs.helper import get_current_time


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


T = TypeVar("T")


class ResponseContext(BaseModel):
    status: int = Field(default=200)
    message: str = Field(default="")
    server_at: int = Field(default_factory=get_current_time)


def get_default_response_message() -> ResponseContext:
    return ResponseContext(status=200, message="", server_at=get_current_time())


class ResponseSchema(BaseModel, Generic[T]):
    data: Optional[T] = Field(...)
    context: ResponseContext = Field(default_factory=get_default_response_message)

    @classmethod
    def from_error(cls, message: str, status: int = 500) -> "ResponseSchema":
        return cls(data=None, context=ResponseContext(status=status, message=message))

    @classmethod
    def from_success(
        cls, data: T, message: str = "", status: int = 200
    ) -> "ResponseSchema[T]":
        return cls(data=data, context=ResponseContext(status=status, message=message))

    def with_context(self, status: int = 200, message: str = "") -> "ResponseSchema":
        self.context.status = status
        self.context.message = message
        return self


def make_api_response(resp: ResponseSchema, status: Optional[int] = None) -> Response:
    resp_dict = resp.model_dump()
    if status is None:
        status = 200
    return jsonify(resp_dict), status
