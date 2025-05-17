from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta

from libs.models import AccountInDB
from services.permission import PermissionService, PermissionError


class BaseDashboardManager:
    """看板数据管理基础类"""

    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象

    def __init__(self, session: Session, account: AccountInDB):
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def check_company_permission(self, company_id: int) -> None:
        """检查用户是否有访问指定公司数据的权限

        Args:
            company_id: 公司ID

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

    def check_subsidiary_permission(self, parent_id: int) -> None:
        """检查用户是否有查看子公司数据的权限

        Args:
            parent_id: 母公司ID

        Raises:
            PermissionError: 如果用户没有查看子公司数据的权限
        """
        if not self._permission.can_view_subsidiary_data(parent_id):
            raise PermissionError("您没有查看子公司数据的权限")

    def get_months_between(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[int, int]]:
        """获取两个日期之间的所有月份列表

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            月份列表，每个元素为(year, month)元组
        """
        months = []
        current_date = start_date

        while current_date <= end_date:
            months.append((current_date.year, current_date.month))

            # 移动到下个月
            current_date = current_date + relativedelta(months=1)

        return months
