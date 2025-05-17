from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from libs.models import AccountInDB

from ._schema import (
    DashboardStats,
    EmployeeOverview,
    RecruitmentStats,
    OrganizationStats,
    BirthdayEmployee,
)
from .base_manager import BaseDashboardManager
from .employee_manager import EmployeeStatsManager
from .recruitment_manager import RecruitmentStatsManager
from .organization_manager import OrganizationStatsManager
from .aggregation_manager import CompanyAggregationManager


# 定义看板服务类
class DashboardService:
    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象

    # 各个Manager实例
    _employee_manager: EmployeeStatsManager
    _recruitment_manager: RecruitmentStatsManager
    _organization_manager: OrganizationStatsManager
    _aggregation_manager: CompanyAggregationManager

    def __init__(self, session: Session, account: AccountInDB):
        """初始化DashboardService

        Args:
            session: 数据库会话对象
            account: 当前登录的用户对象
        """
        self.session = session
        self.account = account

        # 初始化各个管理器实例
        self._employee_manager = EmployeeStatsManager(session, account)
        self._recruitment_manager = RecruitmentStatsManager(session, account)
        self._organization_manager = OrganizationStatsManager(session, account)
        self._aggregation_manager = CompanyAggregationManager(session, account)

    def get_dashboard_stats(
        self, company_id: int, start_time: int, end_time: int
    ) -> DashboardStats:
        """获取单个公司的仪表盘统计数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            仪表盘统计数据，包含员工概览、招聘统计和组织发展数据
        """
        # 获取员工概览
        employee_overview = self._employee_manager.get_employee_overview(
            company_id, start_time, end_time
        )

        # 获取招聘统计
        recruitment_stats = self._recruitment_manager.get_recruitment_stats(
            company_id, start_time, end_time
        )

        # 获取组织发展
        organization_stats = self._organization_manager.get_organization_stats(
            company_id, start_time, end_time
        )

        # 组合数据
        return DashboardStats(
            **employee_overview.model_dump(),
            **recruitment_stats.model_dump(),
            **organization_stats.model_dump(),
        )

    def get_employee_overview(
        self, company_id: int, start_time: int, end_time: int
    ) -> EmployeeOverview:
        """获取员工概览数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            员工概览数据
        """
        return self._employee_manager.get_employee_overview(
            company_id, start_time, end_time
        )

    def get_recruitment_stats(
        self, company_id: int, start_time: int, end_time: int
    ) -> RecruitmentStats:
        """获取招聘统计数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            招聘统计数据
        """
        return self._recruitment_manager.get_recruitment_stats(
            company_id, start_time, end_time
        )

    def get_organization_stats(
        self, company_id: int, start_time: int, end_time: int
    ) -> OrganizationStats:
        """获取组织发展数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            组织发展数据
        """
        return self._organization_manager.get_organization_stats(
            company_id, start_time, end_time
        )

    def get_birthday_employees(
        self, company_id: int, start_time: int, end_time: int
    ) -> List[BirthdayEmployee]:
        """获取生日员工数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            生日员工数据列表
        """
        return self._employee_manager.get_birthday_employees(
            company_id, start_time, end_time
        )

    def get_subsidiaries_stats(
        self, parent_id: int, subsidiary_ids: List[int], start_time: int, end_time: int
    ) -> DashboardStats:
        """获取子公司聚合统计数据

        Args:
            parent_id: 母公司ID
            subsidiary_ids: 子公司ID列表，为空时获取所有子公司
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            子公司聚合统计数据
        """
        return self._aggregation_manager.get_subsidiaries_stats(
            parent_id, subsidiary_ids, start_time, end_time, self
        )

    def _get_months_between(
        self, start_date: datetime, end_date: datetime
    ) -> List[tuple]:
        """获取两个日期之间的所有月份列表

        此方法保留用于兼容旧代码，实际上应该使用BaseDashboardManager.get_months_between

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            月份列表，每个元素为(year, month)元组
        """
        base_manager = BaseDashboardManager(self.session, self.account)
        return base_manager.get_months_between(start_date, end_date)
