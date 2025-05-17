from sqlalchemy import func
from datetime import datetime

from libs.models import (
    CandidateInDB,
    DepartmentInDB,
    CandidateStatus,
)
from ._schema import (
    CandidateStatusDistribution,
    DepartmentRecruitment,
    RecruitmentStats,
)
from .base_manager import BaseDashboardManager


class RecruitmentStatsManager(BaseDashboardManager):
    """招聘统计数据管理类"""

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
        self.check_company_permission(company_id)

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
