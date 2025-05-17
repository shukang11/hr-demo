from typing import List
import logging
from sqlalchemy import select, exists

from libs.models import CompanyInDB
from ._schema import (
    DashboardStats,
    GenderDistribution,
    DepartmentDistribution,
    AgeDistribution,
    CandidateStatusDistribution,
    DepartmentRecruitment,
    MonthlyCount,
    PositionDistribution,
    TenureDistribution,
)
from .base_manager import BaseDashboardManager


class CompanyAggregationManager(BaseDashboardManager):
    """公司数据聚合管理类"""

    def get_subsidiaries_stats(
        self,
        parent_id: int,
        subsidiary_ids: List[int],
        start_time: int,
        end_time: int,
        dashboard_service,
    ) -> DashboardStats:
        """获取多个子公司的聚合统计数据

        Args:
            parent_id: 母公司ID
            subsidiary_ids: 子公司ID列表
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            dashboard_service: DashboardService实例，用于获取各公司统计数据

        Returns:
            包含多个子公司聚合的统计数据

        Raises:
            PermissionError: 如果用户没有查看子公司数据的权限
        """
        # 检查权限
        self.check_subsidiary_permission(parent_id)

        # 如果没有提供子公司ID，则获取所有子公司
        if not subsidiary_ids:
            # 查询所有子公司
            subsidiaries = (
                self.session.query(CompanyInDB)
                .filter(CompanyInDB.parent_id == parent_id)
                .all()
            )
            subsidiary_ids = [sub.id for sub in subsidiaries]
            # 如果需要包括母公司自身，添加母公司ID
            if parent_id not in subsidiary_ids:
                subsidiary_ids.append(parent_id)

        # 存储所有子公司的聚合数据
        all_stats = []

        # 获取每个子公司的统计数据
        for company_id in subsidiary_ids:
            try:
                # 获取该公司的统计数据
                company_stats = dashboard_service.get_dashboard_stats(
                    company_id, start_time, end_time
                )
                all_stats.append(company_stats)
            except Exception as e:
                # 记录错误但继续处理其他公司
                logging.error(f"获取公司ID {company_id} 统计数据失败: {e}")
                continue

        # 添加母公司自身的数据
        try:
            if parent_id not in subsidiary_ids:
                parent_stats = dashboard_service.get_dashboard_stats(
                    parent_id, start_time, end_time
                )
                all_stats.append(parent_stats)
        except Exception as e:
            logging.error(f"获取母公司ID {parent_id} 统计数据失败: {e}")

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
        age_ranges = ["20岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁以上"]
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
        tenure_ranges = ["1年以内", "1-3年", "3-5年", "5-10年", "10年以上"]
        tenure_distribution.sort(
            key=lambda x: tenure_ranges.index(x.range)
            if x.range in tenure_ranges
            else 999
        )

        # 计算最终转化率（加权平均）
        final_conversion_rate = 0
        if total_conversion_weight > 0:
            final_conversion_rate = weighted_conversion_rate / total_conversion_weight

        # 聚合部门增长趋势
        department_trends = {}
        all_departments = set()
        all_months = set()

        # 收集所有部门和月份
        for stats in stats_list:
            for dept_trend in stats.departmentGrowthTrend:
                all_departments.add(dept_trend.department)
                for month_data in dept_trend.trend:
                    all_months.add(month_data.month)

        # 初始化部门趋势数据结构
        for dept in all_departments:
            department_trends[dept] = {}
            for month in all_months:
                department_trends[dept][month] = 0

        # 填充数据
        for stats in stats_list:
            for dept_trend in stats.departmentGrowthTrend:
                dept = dept_trend.department
                for month_data in dept_trend.trend:
                    month = month_data.month
                    department_trends[dept][month] += month_data.count

        # 重新格式化为 API 数据结构
        department_growth_trend = []
        for dept, months in department_trends.items():
            trend_data = []
            for month, count in sorted(months.items()):
                trend_data.append(MonthlyCount(month=month, count=count))

            department_growth_trend.append({"department": dept, "trend": trend_data})

        # 返回聚合后的结果
        return DashboardStats(
            totalEmployees=total_employees,
            departmentDistribution=department_distribution,
            genderDistribution=gender_distribution,
            ageDistribution=age_distribution,
            candidateStatusDistribution=candidate_status_distribution,
            monthlyInterviews=monthly_interviews,
            conversionRate=round(final_conversion_rate, 2),
            departmentRecruitmentTop5=department_recruitment_top5,
            employeeGrowthTrend=employee_growth_trend,
            departmentGrowthTrend=department_growth_trend,
            positionDistribution=position_distribution,
            tenureDistribution=tenure_distribution,
        )
