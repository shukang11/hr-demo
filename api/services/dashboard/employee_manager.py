from typing import List
from sqlalchemy import func, case
from datetime import datetime

from libs.models import EmployeeInDB, DepartmentInDB
from libs.models.employee_position import EmployeePositionInDB
from ._schema import (
    DepartmentDistribution,
    GenderDistribution,
    AgeDistribution,
    EmployeeOverview,
    BirthdayEmployee as BirthdayEmployeeSchema,
)
from .base_manager import BaseDashboardManager


class EmployeeStatsManager(BaseDashboardManager):
    """员工统计数据管理类"""

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
        self.check_company_permission(company_id)

        # 查询总员工数
        total_employees = (
            self.session.query(func.count(EmployeeInDB.id))
            .filter(EmployeeInDB.company_id == company_id)
            .scalar()
            or 0
        )

        # 查询部门分布
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
        if not gender_query:
            return EmployeeOverview(
                totalEmployees=total_employees,
                departmentDistribution=department_distribution,
                genderDistribution=GenderDistribution(male=0, female=0, unknown=0),
                ageDistribution=[],
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

    def get_birthday_employees(
        self, company_id: int, start_time: int, end_time: int
    ) -> List[BirthdayEmployeeSchema]:
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
        self.check_company_permission(company_id)

        # 转换时间戳为日期
        start_date = datetime.fromtimestamp(start_time / 1000)
        end_date = datetime.fromtimestamp(end_time / 1000)

        # 提取月日对比值 (月*100+日)
        start_md = start_date.month * 100 + start_date.day
        end_md = end_date.month * 100 + end_date.day

        # 查询员工生日信息
        from libs.models import PositionInDB

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
                from datetime import date, time as dt_time

                current_year = datetime.now().year
                if isinstance(employee.birthdate, date) and not isinstance(
                    employee.birthdate, datetime
                ):
                    # 如果是date对象，转换为datetime
                    birthday_date = datetime.combine(
                        employee.birthdate.replace(year=current_year), dt_time()
                    )
                else:
                    # 如果已经是datetime对象
                    birthday_date = employee.birthdate.replace(year=current_year)

                timestamp = int(birthday_date.timestamp() * 1000)

                birthday_employees.append(
                    BirthdayEmployeeSchema(
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
