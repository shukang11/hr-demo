from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, case, extract, text, exists, Integer
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar
import logging

# 导入数据库模型
from libs.models import (
    EmployeeInDB,
    AccountInDB,
    DepartmentInDB,
    PositionInDB,
    CandidateInDB,
    CandidateStatus,
    CompanyInDB,
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

        # 导入员工职位模型
        from libs.models.employee_position import EmployeePositionInDB

        # 提取月日对比值 (月*100+日)
        start_md = start_date.month * 100 + start_date.day
        end_md = end_date.month * 100 + end_date.day

        # 使用子查询来处理月份和日期
        query = (
            self.session.query(
                EmployeeInDB.id,
                EmployeeInDB.name,
                DepartmentInDB.name.label("department"),
                PositionInDB.name.label("position"),
                EmployeeInDB.birthdate,
            )
            .outerjoin(
                EmployeePositionInDB,
                EmployeeInDB.id == EmployeePositionInDB.employee_id,
            )
            .outerjoin(
                DepartmentInDB, EmployeePositionInDB.department_id == DepartmentInDB.id
            )
            .outerjoin(
                PositionInDB, EmployeePositionInDB.position_id == PositionInDB.id
            )
            .filter(EmployeeInDB.company_id == company_id)
            .filter(EmployeeInDB.birthdate.isnot(None))
        )

        # 将查询结果转为列表，并在Python中过滤
        employees = query.all()
        birthday_employees = []

        for employee in employees:
            # 提取生日的月和日
            birth_month = employee.birthdate.month
            birth_day = employee.birthdate.day
            birth_md = birth_month * 100 + birth_day

            # 判断是否在范围内
            is_in_range = False
            if start_md <= end_md:  # 日期范围不跨年
                if start_md <= birth_md <= end_md:
                    is_in_range = True
            else:  # 日期范围跨年 (例如 12月至次年2月)
                if birth_md >= start_md or birth_md <= end_md:
                    is_in_range = True

            if is_in_range:
                # 计算正确的时间戳 (使用生日的月日与当前年份组合)
                # 修复: 处理date对象，将其转换为datetime后再获取时间戳
                current_year = datetime.now().year
                if isinstance(employee.birthdate, date) and not isinstance(
                    employee.birthdate, datetime
                ):
                    # 如果是date对象，转换为datetime
                    from datetime import time as dt_time

                    birthday_date = datetime.combine(
                        employee.birthdate.replace(year=current_year), dt_time()
                    )
                else:
                    # 如果已经是datetime对象
                    birthday_date = employee.birthdate.replace(year=current_year)

                timestamp = int(birthday_date.timestamp() * 1000)

                birthday_employees.append(
                    BirthdayEmployee(
                        id=employee.id,
                        name=employee.name,
                        department=employee.department
                        if employee.department
                        else "未分配",
                        position=employee.position if employee.position else "未分配",
                        birthdate=timestamp,
                    )
                )

        # 按照生日排序 (先按月，再按日)
        birthday_employees.sort(
            key=lambda x: (
                datetime.fromtimestamp(x.birthdate / 1000).month,
                datetime.fromtimestamp(x.birthdate / 1000).day,
            )
        )

        return birthday_employees

    def get_subsidiaries_stats(
        self, parent_id: int, subsidiary_ids: List[int], start_time: int, end_time: int
    ) -> DashboardStats:
        """获取多个子公司的聚合统计数据

        Args:
            parent_id: 母公司ID
            subsidiary_ids: 子公司ID列表
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            包含多个子公司聚合的统计数据

        Raises:
            PermissionError: 如果用户没有查看子公司数据的权限
        """
        # 检查权限
        if not self._permission.can_view_subsidiary_data(parent_id):
            raise PermissionError("您没有查看子公司数据的权限")

        # 如果没有提供子公司ID，则获取所有子公司
        if not subsidiary_ids:
            # 查询所有子公司
            stmt = select(CompanyInDB.id).where(CompanyInDB.parent_id == parent_id)
            result = self.session.execute(stmt).scalars().all()
            subsidiary_ids = list(result)

            if not subsidiary_ids:
                return self.get_dashboard_stats(parent_id, start_time, end_time)

        # 存储所有子公司的聚合数据
        all_stats = []

        # 获取每个子公司的统计数据
        for company_id in subsidiary_ids:
            try:
                # 检查这是否真的是指定母公司的子公司
                stmt = select(
                    exists().where(
                        CompanyInDB.id == company_id, CompanyInDB.parent_id == parent_id
                    )
                )
                is_subsidiary = self.session.execute(stmt).scalar()

                if not is_subsidiary:
                    # 如果不是子公司，则跳过
                    continue

                # 获取该子公司的统计数据
                company_stats = self.get_dashboard_stats(
                    company_id, start_time, end_time
                )
                all_stats.append(company_stats)

            except Exception as e:
                # 记录错误但继续处理其他子公司
                logging.error(f"获取子公司 {company_id} 的统计数据失败: {e}")
                continue

        # 添加母公司自身的数据
        try:
            parent_stats = self.get_dashboard_stats(parent_id, start_time, end_time)
            all_stats.append(parent_stats)
        except Exception as e:
            logging.error(f"获取母公司 {parent_id} 的统计数据失败: {e}")

        # 如果没有数据返回空对象
        if not all_stats:
            return DashboardStats(
                totalEmployees=0,
                departmentDistribution=[],
                genderDistribution=GenderDistribution(male=0, female=0, unknown=0),
                ageDistribution=[],
                candidateStatusDistribution=[],
                monthlyInterviews=0,
                conversionRate=0,
                departmentRecruitmentTop5=[],
                employeeGrowthTrend=[],
                departmentGrowthTrend=[],
                positionDistribution=[],
                tenureDistribution=[],
            )

        # 聚合所有数据
        return self._aggregate_dashboard_stats(all_stats)

    def _aggregate_dashboard_stats(
        self, stats_list: List[DashboardStats]
    ) -> DashboardStats:
        """聚合多个公司的统计数据

        Args:
            stats_list: 包含多个公司统计数据的列表

        Returns:
            聚合后的统计数据
        """
        # 如果列表为空，返回空的统计数据
        if not stats_list:
            return DashboardStats(
                totalEmployees=0,
                departmentDistribution=[],
                genderDistribution=GenderDistribution(male=0, female=0, unknown=0),
                ageDistribution=[],
                candidateStatusDistribution=[],
                monthlyInterviews=0,
                conversionRate=0,
                departmentRecruitmentTop5=[],
                employeeGrowthTrend=[],
                departmentGrowthTrend=[],
                positionDistribution=[],
                tenureDistribution=[],
            )

        # 如果只有一个公司，直接返回其数据
        if len(stats_list) == 1:
            return stats_list[0]

        # 初始化聚合数据
        total_employees = 0
        department_map = {}
        gender_distribution = GenderDistribution(male=0, female=0, unknown=0)
        age_map = {}
        candidate_status_map = {}
        monthly_interviews = 0
        weighted_conversion_rate = 0
        total_conversion_weight = 0
        department_recruitment_map = {}
        employee_growth_map = {}
        position_map = {}
        tenure_map = {}

        # 聚合各项数据
        for stats in stats_list:
            # 员工总数
            total_employees += stats.totalEmployees

            # 部门分布
            for dept in stats.departmentDistribution:
                if dept.department in department_map:
                    department_map[dept.department] += dept.count
                else:
                    department_map[dept.department] = dept.count

            # 性别分布
            gender_distribution.male += stats.genderDistribution.male
            gender_distribution.female += stats.genderDistribution.female
            gender_distribution.unknown += stats.genderDistribution.unknown

            # 年龄分布
            for age in stats.ageDistribution:
                if age.range in age_map:
                    age_map[age.range] += age.count
                else:
                    age_map[age.range] = age.count

            # 候选人状态分布
            for status in stats.candidateStatusDistribution:
                if status.status in candidate_status_map:
                    candidate_status_map[status.status] += status.count
                else:
                    candidate_status_map[status.status] = status.count

            # 月度面试
            monthly_interviews += stats.monthlyInterviews

            # 转化率（加权平均）
            if stats.monthlyInterviews > 0:
                weighted_conversion_rate += (
                    stats.conversionRate * stats.monthlyInterviews
                )
                total_conversion_weight += stats.monthlyInterviews

            # 部门招聘
            for dept in stats.departmentRecruitmentTop5:
                if dept.department in department_recruitment_map:
                    department_recruitment_map[dept.department] += dept.openPositions
                else:
                    department_recruitment_map[dept.department] = dept.openPositions

            # 员工增长趋势
            for growth in stats.employeeGrowthTrend:
                if growth.month in employee_growth_map:
                    employee_growth_map[growth.month] += growth.count
                else:
                    employee_growth_map[growth.month] = growth.count

            # 职位分布
            for pos in stats.positionDistribution:
                if pos.position in position_map:
                    position_map[pos.position] += pos.count
                else:
                    position_map[pos.position] = pos.count

            # 任职时长分布
            for tenure in stats.tenureDistribution:
                if tenure.range in tenure_map:
                    tenure_map[tenure.range] += tenure.count
                else:
                    tenure_map[tenure.range] = tenure.count

        # 构建聚合后的数据结构
        department_distribution = [
            DepartmentDistribution(department=dept, count=count)
            for dept, count in department_map.items()
        ]
        department_distribution.sort(key=lambda x: x.count, reverse=True)

        age_distribution = [
            AgeDistribution(range=age_range, count=count)
            for age_range, count in age_map.items()
        ]
        # 按年龄范围排序
        age_ranges = ["0-18", "18-25", "26-35", "36-45", "46-55", "56+"]
        age_distribution.sort(
            key=lambda x: age_ranges.index(x.range) if x.range in age_ranges else 999
        )

        candidate_status_distribution = [
            CandidateStatusDistribution(status=status, count=count)
            for status, count in candidate_status_map.items()
        ]
        candidate_status_distribution.sort(key=lambda x: x.count, reverse=True)

        department_recruitment = [
            DepartmentRecruitment(department=dept, openPositions=count)
            for dept, count in department_recruitment_map.items()
        ]
        department_recruitment.sort(key=lambda x: x.openPositions, reverse=True)
        department_recruitment_top5 = department_recruitment[:5]

        employee_growth_trend = [
            MonthlyCount(month=month, count=count)
            for month, count in employee_growth_map.items()
        ]
        # 按月份排序
        employee_growth_trend.sort(key=lambda x: x.month)

        position_distribution = [
            PositionDistribution(position=pos, count=count)
            for pos, count in position_map.items()
        ]
        position_distribution.sort(key=lambda x: x.count, reverse=True)

        tenure_distribution = [
            TenureDistribution(range=tenure, count=count)
            for tenure, count in tenure_map.items()
        ]
        # 按时长范围排序
        tenure_ranges = ["<1年", "1-3年", "3-5年", "5-10年", ">10年"]
        tenure_distribution.sort(
            key=lambda x: tenure_ranges.index(x.range)
            if x.range in tenure_ranges
            else 999
        )

        # 计算最终转化率（加权平均）
        final_conversion_rate = 0
        if total_conversion_weight > 0:
            final_conversion_rate = weighted_conversion_rate / total_conversion_weight

        # 部门增长趋势暂不聚合，使用第一个公司的数据
        department_growth_trend = (
            stats_list[0].departmentGrowthTrend if stats_list else []
        )

        # 返回聚合后的结果
        return DashboardStats(
            totalEmployees=total_employees,
            departmentDistribution=department_distribution,
            genderDistribution=gender_distribution,
            ageDistribution=age_distribution,
            candidateStatusDistribution=candidate_status_distribution,
            monthlyInterviews=monthly_interviews,
            conversionRate=final_conversion_rate,
            departmentRecruitmentTop5=department_recruitment_top5,
            employeeGrowthTrend=employee_growth_trend,
            departmentGrowthTrend=department_growth_trend,
            positionDistribution=position_distribution,
            tenureDistribution=tenure_distribution,
        )

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
