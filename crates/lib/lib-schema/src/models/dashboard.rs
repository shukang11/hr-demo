use serde::{Deserialize, Serialize};
use chrono::naive::serde::ts_milliseconds::deserialize as from_milli_ts;
use chrono::naive::serde::ts_milliseconds::serialize as to_milli_ts;
use chrono::NaiveDateTime;

/// 时间范围
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DateRange {
    /// 开始时间
    #[serde(
        serialize_with = "to_milli_ts",
        deserialize_with = "from_milli_ts"
    )]
    pub start_time: NaiveDateTime,
    
    /// 结束时间
    #[serde(
        serialize_with = "to_milli_ts",
        deserialize_with = "from_milli_ts"
    )]
    pub end_time: NaiveDateTime,
}

/// 部门分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepartmentDistribution {
    /// 部门名称
    pub department: String,
    /// 员工数量
    pub count: i64,
}

/// 性别分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GenderDistribution {
    /// 男性数量
    pub male: i64,
    /// 女性数量
    pub female: i64,
    /// 未知性别数量
    pub unknown: i64,
}

/// 年龄分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgeDistribution {
    /// 年龄范围（如：20-25岁）
    pub range: String,
    /// 员工数量
    pub count: i64,
}

/// 候选人状态分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CandidateStatusDistribution {
    /// 状态（如：待面试、已面试、已入职等）
    pub status: String,
    /// 候选人数量
    pub count: i64,
}

/// 部门招聘需求统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepartmentRecruitment {
    /// 部门名称
    pub department: String,
    /// 开放职位数量
    #[serde(rename = "openPositions")]
    pub open_positions: i64,
}

/// 月度统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonthlyCount {
    /// 月份（格式：YYYY-MM）
    pub month: String,
    /// 数量
    pub count: i64,
}

/// 部门人员变化趋势
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepartmentTrend {
    /// 部门名称
    pub department: String,
    /// 月度变化趋势
    pub trend: Vec<MonthlyCount>,
}

/// 职位分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PositionDistribution {
    /// 职位名称
    pub position: String,
    /// 员工数量
    pub count: i64,
}

/// 入职时长分布统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TenureDistribution {
    /// 时长范围（如：1年以下、1-3年等）
    pub range: String,
    /// 员工数量
    pub count: i64,
}

/// 看板统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardStats {
    /// 员工总数
    #[serde(rename = "totalEmployees")]
    pub total_employees: i64,
    
    /// 部门分布
    #[serde(rename = "departmentDistribution")]
    pub department_distribution: Vec<DepartmentDistribution>,
    
    /// 性别分布
    #[serde(rename = "genderDistribution")]
    pub gender_distribution: GenderDistribution,
    
    /// 年龄分布
    #[serde(rename = "ageDistribution")]
    pub age_distribution: Vec<AgeDistribution>,
    
    /// 候选人状态分布
    #[serde(rename = "candidateStatusDistribution")]
    pub candidate_status_distribution: Vec<CandidateStatusDistribution>,
    
    /// 本月面试数量
    #[serde(rename = "monthlyInterviews")]
    pub monthly_interviews: i64,
    
    /// 面试转化率（入职人数/面试总人数）
    #[serde(rename = "conversionRate")]
    pub conversion_rate: f32,
    
    /// 部门招聘需求TOP5
    #[serde(rename = "departmentRecruitmentTop5")]
    pub department_recruitment_top5: Vec<DepartmentRecruitment>,
    
    /// 员工增长趋势（近12个月）
    #[serde(rename = "employeeGrowthTrend")]
    pub employee_growth_trend: Vec<MonthlyCount>,
    
    /// 部门人员变化趋势（近12个月）
    #[serde(rename = "departmentGrowthTrend")]
    pub department_growth_trend: Vec<DepartmentTrend>,
    
    /// 职位分布
    #[serde(rename = "positionDistribution")]
    pub position_distribution: Vec<PositionDistribution>,
    
    /// 入职时长分布
    #[serde(rename = "tenureDistribution")]
    pub tenure_distribution: Vec<TenureDistribution>,
}

impl Default for DashboardStats {
    fn default() -> Self {
        Self {
            total_employees: 0,
            department_distribution: Vec::new(),
            gender_distribution: GenderDistribution {
                male: 0,
                female: 0,
                unknown: 0,
            },
            age_distribution: Vec::new(),
            candidate_status_distribution: Vec::new(),
            monthly_interviews: 0,
            conversion_rate: 0.0,
            department_recruitment_top5: Vec::new(),
            employee_growth_trend: Vec::new(),
            department_growth_trend: Vec::new(),
            position_distribution: Vec::new(),
            tenure_distribution: Vec::new(),
        }
    }
}

/// 人员概览统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmployeeOverview {
    /// 员工总数
    #[serde(rename = "totalEmployees")]
    pub total_employees: i64,
    
    /// 部门分布
    #[serde(rename = "departmentDistribution")]
    pub department_distribution: Vec<DepartmentDistribution>,
    
    /// 性别分布
    #[serde(rename = "genderDistribution")]
    pub gender_distribution: GenderDistribution,
    
    /// 年龄分布
    #[serde(rename = "ageDistribution")]
    pub age_distribution: Vec<AgeDistribution>,
}

/// 招聘概况统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecruitmentStats {
    /// 候选人状态分布
    #[serde(rename = "candidateStatusDistribution")]
    pub candidate_status_distribution: Vec<CandidateStatusDistribution>,
    
    /// 本月面试数量
    #[serde(rename = "monthlyInterviews")]
    pub monthly_interviews: i64,
    
    /// 面试转化率（入职人数/面试总人数）
    #[serde(rename = "conversionRate")]
    pub conversion_rate: f32,
    
    /// 部门招聘需求TOP5
    #[serde(rename = "departmentRecruitmentTop5")]
    pub department_recruitment_top5: Vec<DepartmentRecruitment>,
}

/// 组织发展统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrganizationStats {
    /// 员工增长趋势（近12个月）
    #[serde(rename = "employeeGrowthTrend")]
    pub employee_growth_trend: Vec<MonthlyCount>,
    
    /// 部门人员变化趋势（近12个月）
    #[serde(rename = "departmentGrowthTrend")]
    pub department_growth_trend: Vec<DepartmentTrend>,
    
    /// 职位分布
    #[serde(rename = "positionDistribution")]
    pub position_distribution: Vec<PositionDistribution>,
    
    /// 入职时长分布
    #[serde(rename = "tenureDistribution")]
    pub tenure_distribution: Vec<TenureDistribution>,
}

/// 生日员工信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BirthdayEmployee {
    /// 员工ID
    pub id: i32,
    /// 员工姓名
    pub name: String,
    /// 部门名称
    pub department: String,
    /// 职位名称
    pub position: String,
    /// 生日日期
    #[serde(
        serialize_with = "to_milli_ts",
        deserialize_with = "from_milli_ts"
    )]
    pub birthdate: NaiveDateTime,
}
