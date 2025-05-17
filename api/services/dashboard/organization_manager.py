from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

from libs.models import (
    EmployeeInDB,
    DepartmentInDB,
    PositionInDB,
)
from libs.models.employee_position import EmployeePositionInDB
from ._schema import (
    MonthlyCount,
    DepartmentTrend,
    PositionDistribution,
    TenureDistribution,
    OrganizationStats,
)
from .base_manager import BaseDashboardManager


class OrganizationStatsManager(BaseDashboardManager):
    """组织结构统计数据管理类"""

    def get_organization_stats(
        self, company_id: int, start_time: int, end_time: int
    ) -> OrganizationStats:
        """获取组织发展统计数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            组织发展数据，包含员工增长趋势、部门增长趋势、职位分布和工龄分布

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        # 检查权限
        self.check_company_permission(company_id)

        # 转换时间戳为日期
        start_date = datetime.fromtimestamp(start_time / 1000)
        end_date = datetime.fromtimestamp(end_time / 1000)

        # 计算员工增长趋势 (按月)
        months = self.get_months_between(start_date, end_date)
        employee_growth_trend = []

        for year, month in months:
            # 获取当月最后一天
            month_end = datetime(
                year, month, calendar.monthrange(year, month)[1], 23, 59, 59
            )

            # 当月在职员工数
            employee_count = (
                self.session.query(func.count(EmployeeInDB.id))
                .filter(
                    EmployeeInDB.company_id == company_id,
                    EmployeeInDB.created_at <= month_end,
                )
                .scalar()
                or 0
            )

            month_str = f"{year}-{month:02d}"
            employee_growth_trend.append(
                MonthlyCount(month=month_str, count=employee_count)
            )

        # 计算部门增长趋势
        department_growth_trend = []

        # 获取所有部门
        departments = (
            self.session.query(DepartmentInDB)
            .filter(DepartmentInDB.company_id == company_id)
            .all()
        )

        for department in departments:
            dept_trend = []

            for year, month in months:
                # 获取当月最后一天
                month_end = datetime(
                    year, month, calendar.monthrange(year, month)[1], 23, 59, 59
                )

                # 当月部门员工数
                dept_emp_count = (
                    self.session.query(func.count(EmployeeInDB.id))
                    .join(
                        EmployeePositionInDB,
                        (EmployeePositionInDB.employee_id == EmployeeInDB.id)
                        & (EmployeePositionInDB.department_id == department.id),
                    )
                    .filter(
                        EmployeeInDB.company_id == company_id,
                        EmployeeInDB.created_at <= month_end,
                    )
                    .scalar()
                    or 0
                )

                month_str = f"{year}-{month:02d}"
                dept_trend.append(MonthlyCount(month=month_str, count=dept_emp_count))

            department_growth_trend.append(
                DepartmentTrend(department=department.name, trend=dept_trend)
            )

        # 查询职位分布
        position_query = (
            self.session.query(PositionInDB.name, func.count(EmployeeInDB.id))
            .join(
                EmployeePositionInDB,
                EmployeePositionInDB.position_id == PositionInDB.id,
            )
            .join(EmployeeInDB, EmployeeInDB.id == EmployeePositionInDB.employee_id)
            .filter(PositionInDB.company_id == company_id)
            .group_by(PositionInDB.name)
            .order_by(func.count(EmployeeInDB.id).desc())
            .all()
        )

        position_distribution = [
            PositionDistribution(position=name, count=count)
            for name, count in position_query
        ]

        # 计算工龄分布
        current_date = datetime.now()

        # 定义工龄范围
        tenure_ranges = [
            ("1年以内", 0, 1),
            ("1-3年", 1, 3),
            ("3-5年", 3, 5),
            ("5-10年", 5, 10),
            ("10年以上", 10, 100),
        ]

        tenure_distribution = []

        for range_name, min_years, max_years in tenure_ranges:
            min_date = current_date - relativedelta(years=max_years)
            max_date = current_date - relativedelta(years=min_years)

            count = (
                self.session.query(func.count(EmployeeInDB.id))
                .filter(
                    EmployeeInDB.company_id == company_id,
                    EmployeeInDB.created_at >= min_date,
                    EmployeeInDB.created_at <= max_date,
                )
                .scalar()
                or 0
            )

            tenure_distribution.append(
                TenureDistribution(range=range_name, count=count)
            )

        return OrganizationStats(
            employeeGrowthTrend=employee_growth_trend,
            departmentGrowthTrend=department_growth_trend,
            positionDistribution=position_distribution,
            tenureDistribution=tenure_distribution,
        )
