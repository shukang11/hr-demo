from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DepartmentDistribution(BaseModel):
    """部门分布信息"""

    department: str = Field(..., description="部门名称")
    count: int = Field(..., description="员工数量")


class GenderDistribution(BaseModel):
    """性别分布信息"""

    male: int = Field(..., description="男性数量")
    female: int = Field(..., description="女性数量")
    unknown: int = Field(..., description="未知性别数量")


class AgeDistribution(BaseModel):
    """年龄分布信息"""

    range: str = Field(..., description="年龄范围")
    count: int = Field(..., description="员工数量")


class CandidateStatusDistribution(BaseModel):
    """候选人状态分布"""

    status: str = Field(..., description="状态名称")
    count: int = Field(..., description="候选人数量")


class DepartmentRecruitment(BaseModel):
    """部门招聘信息"""

    department: str = Field(..., description="部门名称")
    openPositions: int = Field(..., description="开放职位数量")


class MonthlyCount(BaseModel):
    """月度计数信息"""

    month: str = Field(..., description="月份，格式为YYYY-MM")
    count: int = Field(..., description="数量")


class DepartmentTrend(BaseModel):
    """部门增长趋势"""

    department: str = Field(..., description="部门名称")
    trend: List[MonthlyCount] = Field(..., description="月度趋势数据")


class PositionDistribution(BaseModel):
    """职位分布信息"""

    position: str = Field(..., description="职位名称")
    count: int = Field(..., description="员工数量")


class TenureDistribution(BaseModel):
    """工龄分布信息"""

    range: str = Field(..., description="工龄范围")
    count: int = Field(..., description="员工数量")


class EmployeeOverview(BaseModel):
    """员工概览信息"""

    totalEmployees: int = Field(..., description="员工总数")
    departmentDistribution: List[DepartmentDistribution] = Field(
        ..., description="部门分布"
    )
    genderDistribution: GenderDistribution = Field(..., description="性别分布")
    ageDistribution: List[AgeDistribution] = Field(..., description="年龄分布")


class RecruitmentStats(BaseModel):
    """招聘统计信息"""

    candidateStatusDistribution: List[CandidateStatusDistribution] = Field(
        ..., description="候选人状态分布"
    )
    monthlyInterviews: int = Field(..., description="每月面试数量")
    conversionRate: float = Field(..., description="转化率")
    departmentRecruitmentTop5: List[DepartmentRecruitment] = Field(
        ..., description="部门招聘Top5"
    )


class OrganizationStats(BaseModel):
    """组织发展统计"""

    employeeGrowthTrend: List[MonthlyCount] = Field(..., description="员工增长趋势")
    departmentGrowthTrend: List[DepartmentTrend] = Field(
        ..., description="部门增长趋势"
    )
    positionDistribution: List[PositionDistribution] = Field(
        ..., description="职位分布"
    )
    tenureDistribution: List[TenureDistribution] = Field(..., description="工龄分布")


class DashboardStats(EmployeeOverview, RecruitmentStats, OrganizationStats):
    """完整看板数据"""

    pass


class BirthdayEmployee(BaseModel):
    """生日员工信息"""

    id: int = Field(..., description="员工ID")
    name: str = Field(..., description="员工姓名")
    department: str = Field(..., description="所在部门")
    position: str = Field(..., description="职位名称")
    birthdate: int = Field(..., description="生日时间戳")
