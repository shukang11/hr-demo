from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, case, extract, text
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar

# 导入数据库模型
from libs.models import (
    EmployeeInDB,
    AccountInDB,
    DepartmentInDB,
    PositionInDB,
    CandidateInDB,
    CandidateStatus,
)
from services.permission import PermissionService, PermissionError

# 导入看板相关的 Pydantic 模型
from ._schema import (
    DepartmentDistribution,
    GenderDistribution,
    AgeDistribution,
    CandidateStatusDistribution,
    DepartmentRecruitment,
    MonthlyCount,
    DepartmentTrend,
    PositionDistribution,
    TenureDistribution,
    EmployeeOverview,
    RecruitmentStats,
    OrganizationStats,
    DashboardStats,
    BirthdayEmployee,
)


# 定义看板服务类
class DashboardService:
    session: Session  # 数据库会话对象
    account: AccountInDB  # 当前登录的用户对象
    _permission: PermissionService  # 权限服务对象

    def __init__(self, session: Session, account: AccountInDB):
        self.session = session
        self.account = account
        self._permission = PermissionService(session, account)

    def get_dashboard_stats(
        self, company_id: int, start_time: int, end_time: int
    ) -> DashboardStats:
        """获取完整的仪表盘统计数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            包含员工概览、招聘统计和组织发展的完整统计数据

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

        # 获取所有统计数据并组合
        employee_overview = self.get_employee_overview(company_id, start_time, end_time)
        recruitment_stats = self.get_recruitment_stats(company_id, start_time, end_time)
        organization_stats = self.get_organization_stats(
            company_id, start_time, end_time
        )

        # 合并数据
        dashboard_data = {
            **employee_overview.dict(),
            **recruitment_stats.dict(),
            **organization_stats.dict(),
        }

        return DashboardStats.parse_obj(dashboard_data)

    def get_employee_overview(
        self, company_id: int, start_time: int, end_time: int
    ) -> EmployeeOverview:
        """获取员工概览数据

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            员工概览数据，包含总人数、部门分布、性别分布和年龄分布

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

        # 查询总员工数
        total_employees = (
            self.session.query(func.count(EmployeeInDB.id))
            .filter(EmployeeInDB.company_id == company_id)
            .scalar()
            or 0
        )

        # 查询部门分布
        from libs.models.employee_position import EmployeePositionInDB

        dept_query = (
            self.session.query(
                DepartmentInDB.name.label("department"),
                func.count(EmployeeInDB.id).label("count"),
            )
            .join(
                EmployeePositionInDB,
                EmployeePositionInDB.department_id == DepartmentInDB.id,
            )
            .join(EmployeeInDB, EmployeeInDB.id == EmployeePositionInDB.employee_id)
            .filter(DepartmentInDB.company_id == company_id)
            .group_by(DepartmentInDB.name)
            .order_by(func.count(EmployeeInDB.id).desc())
        )

        department_distribution = [
            DepartmentDistribution(department=row[0], count=row[1])
            for row in dept_query
        ]

        # 查询性别分布
        gender_query = (
            self.session.query(
                func.sum(case((EmployeeInDB.gender == 1, 1), else_=0)).label("male"),
                func.sum(case((EmployeeInDB.gender == 2, 1), else_=0)).label("female"),
                func.sum(case((EmployeeInDB.gender == 0, 1), else_=0)).label("unknown"),
            )
            .filter(EmployeeInDB.company_id == company_id)
            .first()
        )

        gender_distribution = GenderDistribution(
            male=gender_query[0] or 0,
            female=gender_query[1] or 0,
            unknown=gender_query[2] or 0,
        )

        # 计算年龄分布
        current_date = datetime.now().date()

        # 定义年龄范围
        age_ranges = [
            ("20岁以下", 0, 19),
            ("20-29岁", 20, 29),
            ("30-39岁", 30, 39),
            ("40-49岁", 40, 49),
            ("50岁以上", 50, 100),
        ]

        age_distribution = []

        for range_name, min_age, max_age in age_ranges:
            min_date = current_date.replace(year=current_date.year - max_age - 1)
            max_date = current_date.replace(year=current_date.year - min_age)

            count = (
                self.session.query(func.count(EmployeeInDB.id))
                .filter(
                    EmployeeInDB.company_id == company_id,
                    EmployeeInDB.birthdate >= min_date,
                    EmployeeInDB.birthdate <= max_date,
                )
                .scalar()
                or 0
            )

            age_distribution.append(AgeDistribution(range=range_name, count=count))

        return EmployeeOverview(
            totalEmployees=total_employees,
            departmentDistribution=department_distribution,
            genderDistribution=gender_distribution,
            ageDistribution=age_distribution,
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
            招聘统计数据，包含候选人状态分布、月面试数、转化率和部门招聘TOP5

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

        # 转换时间戳为日期
        start_date = datetime.fromtimestamp(start_time / 1000)
        end_date = datetime.fromtimestamp(end_time / 1000)

        # 查询候选人状态分布
        status_query = (
            self.session.query(CandidateInDB.status, func.count(CandidateInDB.id))
            .filter(
                CandidateInDB.company_id == company_id,
                CandidateInDB.created_at.between(start_date, end_date),
            )
            .group_by(CandidateInDB.status)
            .all()
        )

        status_distribution = [
            CandidateStatusDistribution(status=status.value, count=count)
            for status, count in status_query
        ]

        # 查询月面试数 (在时间范围内的面试总数)
        monthly_interviews = (
            self.session.query(func.count(CandidateInDB.id))
            .filter(
                CandidateInDB.company_id == company_id,
                CandidateInDB.interview_date.between(start_date, end_date),
            )
            .scalar()
            or 0
        )

        # 计算转化率 (已接受/总面试数)
        total_interviews = (
            self.session.query(func.count(CandidateInDB.id))
            .filter(
                CandidateInDB.company_id == company_id,
                CandidateInDB.status != CandidateStatus.PENDING,
                CandidateInDB.created_at.between(start_date, end_date),
            )
            .scalar()
            or 0
        )

        accepted_count = (
            self.session.query(func.count(CandidateInDB.id))
            .filter(
                CandidateInDB.company_id == company_id,
                CandidateInDB.status == CandidateStatus.ACCEPTED,
                CandidateInDB.created_at.between(start_date, end_date),
            )
            .scalar()
            or 0
        )

        conversion_rate = (
            (accepted_count / total_interviews) * 100 if total_interviews > 0 else 0
        )

        # 查询部门招聘Top5
        dept_recruitment_query = (
            self.session.query(DepartmentInDB.name, func.count(CandidateInDB.id))
            .join(
                CandidateInDB,
                (DepartmentInDB.id == CandidateInDB.department_id)
                & (
                    CandidateInDB.status.in_(
                        [CandidateStatus.PENDING, CandidateStatus.SCHEDULED]
                    )
                )
                & (CandidateInDB.created_at.between(start_date, end_date)),
            )
            .filter(DepartmentInDB.company_id == company_id)
            .group_by(DepartmentInDB.name)
            .order_by(func.count(CandidateInDB.id).desc())
            .limit(5)
            .all()
        )

        department_recruitment = [
            DepartmentRecruitment(department=dept_name, openPositions=count)
            for dept_name, count in dept_recruitment_query
        ]

        return RecruitmentStats(
            candidateStatusDistribution=status_distribution,
            monthlyInterviews=monthly_interviews,
            conversionRate=round(conversion_rate, 2),
            departmentRecruitmentTop5=department_recruitment,
        )

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
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

        # 转换时间戳为日期
        start_date = datetime.fromtimestamp(start_time / 1000)
        end_date = datetime.fromtimestamp(end_time / 1000)

        # 计算员工增长趋势 (按月)
        months = self._get_months_between(start_date, end_date)
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
                from libs.models.employee_position import EmployeePositionInDB

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
        from libs.models.employee_position import EmployeePositionInDB

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

    def get_birthday_employees(
        self, company_id: int, start_time: int, end_time: int
    ) -> List[BirthdayEmployee]:
        """获取在指定时间范围内过生日的员工

        Args:
            company_id: 公司ID
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            员工列表，包含基本信息和生日

        Raises:
            PermissionError: 如果用户没有访问指定公司数据的权限
        """
        # 检查权限
        if not self._permission.can_manage_company(company_id):
            raise PermissionError("您没有访问该公司数据的权限")

        # 转换时间戳为日期
        start_date = datetime.fromtimestamp(start_time / 1000)
        end_date = datetime.fromtimestamp(end_time / 1000)

        # 提取出生日的月份和日期，用于查询在指定时间范围内过生日的员工
        # SQLite 版本：使用 strftime 函数代替 MySQL 的 MONTH 和 DAY 函数
        stmt = text("""
            SELECT e.id, e.name, d.name as department, p.name as position, 
                   strftime('%s', e.birthdate) * 1000 as birthdate
            FROM employee e
            LEFT JOIN employee_position ep ON e.id = ep.employee_id
            LEFT JOIN department d ON ep.department_id = d.id
            LEFT JOIN position p ON ep.position_id = p.id
            WHERE e.company_id = :company_id
            AND e.birthdate IS NOT NULL
            AND (
                (strftime('%m', e.birthdate) > strftime('%m', :start_date) OR 
                 (strftime('%m', e.birthdate) = strftime('%m', :start_date) AND strftime('%d', e.birthdate) >= strftime('%d', :start_date)))
                OR
                (strftime('%m', e.birthdate) < strftime('%m', :end_date) OR 
                 (strftime('%m', e.birthdate) = strftime('%m', :end_date) AND strftime('%d', e.birthdate) <= strftime('%d', :end_date)))
            )
            ORDER BY strftime('%m', e.birthdate), strftime('%d', e.birthdate)
        """)

        result = self.session.execute(
            stmt,
            {"company_id": company_id, "start_date": start_date, "end_date": end_date},
        )

        birthday_employees = []
        for row in result:
            birthday_employees.append(
                BirthdayEmployee(
                    id=row[0],
                    name=row[1],
                    department=row[2] if row[2] else "未分配",
                    position=row[3] if row[3] else "未分配",
                    birthdate=row[4],
                )
            )

        return birthday_employees

    def _get_months_between(
        self, start_date: datetime, end_date: datetime
    ) -> List[tuple]:
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
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)

        return months
