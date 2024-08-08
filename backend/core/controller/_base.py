from abc import ABC
from typing import Optional
from sqlalchemy.orm import Session


class BaseController(ABC):
    # 操作员
    operator_id: Optional[int]

    session: Session

    def __init__(self, session: Session) -> None:
        self.session = session

    # 设定操作员. 用于判断是否有权限进行操作 / 生成日志
    def update_operator(self, operator: int) -> None:
        self.operator_id = operator
