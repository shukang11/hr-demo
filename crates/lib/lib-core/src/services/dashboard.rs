use chrono::{Datelike, NaiveDate, NaiveDateTime};
use lib_entity::{
    candidate::{self, CandidateStatus, Entity as Candidate},
    department::{self, Entity as Department},
    employee::{self, Entity as Employee, Gender},
    employee_position::{self, Entity as EmployeePosition},
    position::{self, Entity as Position},
};
use lib_schema::models::dashboard::*;
use sea_orm::{prelude::*, DatabaseConnection, DbErr, EntityTrait, QueryFilter, QueryOrder};

/// 年龄范围定义
const AGE_RANGES: &[(&str, i32, i32)] = &[
    ("未设置", -1, -1),
    ("20岁以下", 0, 20),
    ("20-25岁", 20, 25),
    ("26-30岁", 26, 30),
    ("31-35岁", 31, 35),
    ("36-40岁", 36, 40),
    ("40岁以上", 40, 200),
];

/// 候选人状态定义
const CANDIDATE_STATUSES: &[(&str, &str)] = &[
    ("new", "待面试"),
    ("interviewing", "面试中"),
    ("offered", "已发offer"),
    ("onboard", "已入职"),
    ("rejected", "已拒绝"),
];

/// 入职时长范围定义（单位：月）
const TENURE_RANGES: [(i64, i64); 5] = [
    (0, 12),    // 1年以下
    (12, 36),   // 1-3年
    (36, 60),   // 3-5年
    (60, 120),  // 5-10年
    (120, 360), // 10年以上
];

/// 入职时长范围名称
const TENURE_RANGE_NAMES: [&str; 5] = ["1年以下", "1-3年", "3-5年", "5-10年", "10年以上"];

/// 看板服务
///
/// 提供看板相关的核心业务功能，包括：
/// - 统计员工数据（总数、部门分布、性别分布、年龄分布等）
/// - 统计招聘数据（候选人状态、面试数量、转化率等）
/// - 统计组织发展趋势（员工增长、部门变化等）
#[derive(Debug)]
pub struct DashboardService {
    db: DatabaseConnection,
}

impl DashboardService {
    /// 创建服务实例
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 获取指定月份的起始和结束时间
    fn get_month_range(date: NaiveDateTime) -> (NaiveDateTime, NaiveDateTime) {
        let start_of_month = NaiveDate::from_ymd_opt(date.year(), date.month(), 1)
            .unwrap()
            .and_hms_opt(0, 0, 0)
            .unwrap();

        let next_month = if date.month() == 12 {
            NaiveDate::from_ymd_opt(date.year() + 1, 1, 1)
        } else {
            NaiveDate::from_ymd_opt(date.year(), date.month() + 1, 1)
        }
        .unwrap()
        .and_hms_opt(0, 0, 0)
        .unwrap();

        (start_of_month, next_month)
    }

    /// 获取前一个月的日期
    fn get_previous_month(date: NaiveDateTime) -> NaiveDateTime {
        if date.month() == 1 {
            NaiveDate::from_ymd_opt(date.year() - 1, 12, 1)
        } else {
            NaiveDate::from_ymd_opt(date.year(), date.month() - 1, 1)
        }
        .unwrap()
        .and_hms_opt(0, 0, 0)
        .unwrap()
    }

    /// 获取月度统计数据
    async fn get_monthly_stats<F>(
        &self,
        company_id: i32,
        date_range: &DateRange,
        filter: F,
    ) -> Result<Vec<MonthlyCount>, DbErr>
    where
        F: Fn(Select<EmployeePosition>) -> Select<EmployeePosition>,
    {
        let mut trend = Vec::new();
        let months = (date_range.end_time.year() * 12 + date_range.end_time.month() as i32)
            - (date_range.start_time.year() * 12 + date_range.start_time.month() as i32);

        let mut current_date = date_range.start_time;

        for _ in 0..=months {
            let next_month = if current_date.month() == 12 {
                NaiveDateTime::new(
                    NaiveDate::from_ymd_opt(current_date.year() + 1, 1, 1).unwrap(),
                    current_date.time(),
                )
            } else {
                NaiveDateTime::new(
                    NaiveDate::from_ymd_opt(current_date.year(), current_date.month() + 1, 1)
                        .unwrap(),
                    current_date.time(),
                )
            };

            let mut query = EmployeePosition::find()
                .filter(employee_position::Column::CompanyId.eq(company_id))
                .filter(employee_position::Column::EntryAt.gte(current_date))
                .filter(employee_position::Column::EntryAt.lt(next_month));

            query = filter(query);

            let count = query.count(&self.db).await? as i64;

            trend.push(MonthlyCount {
                month: format!("{}-{:02}", current_date.year(), current_date.month()),
                count,
            });

            current_date = next_month;
        }

        Ok(trend)
    }

    /// 获取员工总数
    async fn get_total_employees(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<i64, DbErr> {
        Ok(EmployeePosition::find()
            .filter(employee_position::Column::CompanyId.eq(company_id))
            .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
            .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
            .count(&self.db)
            .await? as i64)
    }

    /// 获取部门分布
    async fn get_department_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<DepartmentDistribution>, DbErr> {
        let mut distribution = Vec::new();
        let departments = Department::find()
            .filter(department::Column::CompanyId.eq(company_id))
            .all(&self.db)
            .await?;

        for dept in departments {
            let count = EmployeePosition::find()
                .filter(employee_position::Column::CompanyId.eq(company_id))
                .filter(employee_position::Column::DepartmentId.eq(dept.id))
                .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
                .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
                .count(&self.db)
                .await? as i64;

            if count > 0 {
                distribution.push(DepartmentDistribution {
                    department: dept.name,
                    count,
                });
            }
        }
        Ok(distribution)
    }

    /// 获取性别分布
    async fn get_gender_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<GenderDistribution, DbErr> {
        let male = Employee::find()
            .inner_join(EmployeePosition)
            .filter(employee_position::Column::CompanyId.eq(company_id))
            .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
            .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
            .filter(employee::Column::Gender.eq(Gender::Male))
            .count(&self.db)
            .await? as i64;

        let female = Employee::find()
            .inner_join(EmployeePosition)
            .filter(employee_position::Column::CompanyId.eq(company_id))
            .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
            .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
            .filter(employee::Column::Gender.eq(Gender::Female))
            .count(&self.db)
            .await? as i64;

        let unknown = Employee::find()
            .inner_join(EmployeePosition)
            .filter(employee_position::Column::CompanyId.eq(company_id))
            .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
            .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
            .filter(employee::Column::Gender.eq(Gender::Unknown))
            .count(&self.db)
            .await? as i64;

        Ok(GenderDistribution {
            male,
            female,
            unknown,
        })
    }

    /// 获取年龄分布
    async fn get_age_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<AgeDistribution>, DbErr> {
        let mut distribution = Vec::new();
        for (range_name, min_age, max_age) in AGE_RANGES {
            let count = if *min_age == -1 && *max_age == -1 {
                // 统计未设置出生日期的员工
                Employee::find()
                    .inner_join(EmployeePosition)
                    .filter(employee_position::Column::CompanyId.eq(company_id))
                    .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
                    .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
                    .filter(employee::Column::Birthdate.is_null())
                    .count(&self.db)
                    .await? as i64
            } else {
                let current_date = date_range.end_time;
                let min_birth_date = current_date
                    .with_year(current_date.year() - max_age)
                    .unwrap();
                let max_birth_date = current_date
                    .with_year(current_date.year() - min_age)
                    .unwrap();

                Employee::find()
                    .inner_join(EmployeePosition)
                    .filter(employee_position::Column::CompanyId.eq(company_id))
                    .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
                    .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
                    .filter(employee::Column::Birthdate.is_not_null())
                    .filter(employee::Column::Birthdate.gte(min_birth_date))
                    .filter(employee::Column::Birthdate.lt(max_birth_date))
                    .count(&self.db)
                    .await? as i64
            };

            distribution.push(AgeDistribution {
                range: range_name.to_string(),
                count,
            });
        }
        Ok(distribution)
    }

    /// 获取候选人状态分布
    async fn get_candidate_status_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<CandidateStatusDistribution>, DbErr> {
        let mut distribution = Vec::new();
        for &(status_key, status_name) in CANDIDATE_STATUSES {
            let count = Candidate::find()
                .filter(candidate::Column::CompanyId.eq(company_id))
                .filter(candidate::Column::CreatedAt.gte(date_range.start_time))
                .filter(candidate::Column::CreatedAt.lte(date_range.end_time))
                .filter(candidate::Column::Status.eq(status_key.to_owned()))
                .count(&self.db)
                .await? as i64;

            distribution.push(CandidateStatusDistribution {
                status: status_name.to_string(),
                count,
            });
        }
        Ok(distribution)
    }

    /// 获取面试数量
    async fn get_monthly_interviews(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<i64, DbErr> {
        Ok(Candidate::find()
            .filter(candidate::Column::CompanyId.eq(company_id))
            .filter(candidate::Column::InterviewDate.gte(date_range.start_time))
            .filter(candidate::Column::InterviewDate.lte(date_range.end_time))
            .count(&self.db)
            .await? as i64)
    }

    /// 计算面试转化率
    async fn get_conversion_rate(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<f32, DbErr> {
        let total_interviews = Candidate::find()
            .filter(candidate::Column::CompanyId.eq(company_id))
            .filter(candidate::Column::InterviewDate.is_not_null())
            .filter(candidate::Column::InterviewDate.gte(date_range.start_time))
            .filter(candidate::Column::InterviewDate.lte(date_range.end_time))
            .count(&self.db)
            .await? as i64;

        let total_onboard = Candidate::find()
            .filter(candidate::Column::CompanyId.eq(company_id))
            .filter(candidate::Column::Status.eq(CandidateStatus::Accepted))
            .filter(candidate::Column::UpdatedAt.gte(date_range.start_time))
            .filter(candidate::Column::UpdatedAt.lte(date_range.end_time))
            .count(&self.db)
            .await? as i64;

        Ok(if total_interviews > 0 {
            total_onboard as f32 / total_interviews as f32
        } else {
            0.0
        })
    }

    /// 获取部门招聘需求TOP5
    async fn get_department_recruitment_top5(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<DepartmentRecruitment>, DbErr> {
        let mut recruitment = Vec::new();
        let departments = Department::find()
            .filter(department::Column::CompanyId.eq(company_id))
            .all(&self.db)
            .await?;

        for dept in departments {
            let open_positions = Candidate::find()
                .filter(candidate::Column::CompanyId.eq(company_id))
                .filter(candidate::Column::DepartmentId.eq(dept.id))
                .filter(candidate::Column::Status.eq("new"))
                .filter(candidate::Column::CreatedAt.gte(date_range.start_time))
                .filter(candidate::Column::CreatedAt.lte(date_range.end_time))
                .count(&self.db)
                .await? as i64;

            if open_positions > 0 {
                recruitment.push(DepartmentRecruitment {
                    department: dept.name,
                    open_positions,
                });
            }
        }
        recruitment.sort_by(|a, b| b.open_positions.cmp(&a.open_positions));
        recruitment.truncate(5);
        Ok(recruitment)
    }

    /// 获取员工增长趋势（近12个月）
    async fn get_employee_growth_trend(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<MonthlyCount>, DbErr> {
        self.get_monthly_stats(company_id, date_range, |query| query)
            .await
    }

    /// 获取部门人员变化趋势
    async fn get_department_growth_trend(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<DepartmentTrend>, DbErr> {
        let mut trends = Vec::new();
        let departments = Department::find()
            .filter(department::Column::CompanyId.eq(company_id))
            .all(&self.db)
            .await?;

        for dept in departments {
            let dept_id = dept.id;
            let trend = self
                .get_monthly_stats(company_id, date_range, |query: Select<EmployeePosition>| {
                    query.filter(employee_position::Column::DepartmentId.eq(dept_id))
                })
                .await?;

            if trend.iter().any(|m| m.count > 0) {
                trends.push(DepartmentTrend {
                    department: dept.name,
                    trend,
                });
            }
        }
        Ok(trends)
    }

    /// 获取职位分布
    async fn get_position_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<PositionDistribution>, DbErr> {
        let mut distribution = Vec::new();
        let positions = Position::find()
            .filter(position::Column::CompanyId.eq(company_id))
            .all(&self.db)
            .await?;

        for pos in positions {
            let count = EmployeePosition::find()
                .filter(employee_position::Column::CompanyId.eq(company_id))
                .filter(employee_position::Column::PositionId.eq(pos.id))
                .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
                .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
                .count(&self.db)
                .await? as i64;

            if count > 0 {
                distribution.push(PositionDistribution {
                    position: pos.name,
                    count,
                });
            }
        }
        Ok(distribution)
    }

    /// 获取入职时长分布
    async fn get_tenure_distribution(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<TenureDistribution>, DbErr> {
        let mut distribution = Vec::new();
        let current_date = date_range.end_time;

        for (i, (min_months, max_months)) in TENURE_RANGES.iter().copied().enumerate() {
            let max_entry_date = if min_months == 0 {
                current_date
            } else {
                current_date - chrono::Duration::days(min_months * 30)
            };

            let min_entry_date = if max_months == 360 {
                NaiveDate::from_ymd_opt(current_date.year() - 30, current_date.month(), 1)
                    .unwrap()
                    .and_hms_opt(0, 0, 0)
                    .unwrap()
            } else {
                current_date - chrono::Duration::days(max_months * 30)
            };

            let count = EmployeePosition::find()
                .filter(employee_position::Column::CompanyId.eq(company_id))
                .filter(employee_position::Column::EntryAt.is_not_null())
                .filter(employee_position::Column::EntryAt.gte(min_entry_date))
                .filter(employee_position::Column::EntryAt.lt(max_entry_date))
                .filter(employee_position::Column::EntryAt.gte(date_range.start_time))
                .filter(employee_position::Column::EntryAt.lte(date_range.end_time))
                .count(&self.db)
                .await? as i64;

            distribution.push(TenureDistribution {
                range: TENURE_RANGE_NAMES[i].to_string(),
                count,
            });
        }
        Ok(distribution)
    }

    /// 获取人员概览统计
    ///
    /// 包含：
    /// - 员工总数
    /// - 部门分布
    /// - 性别分布
    /// - 年龄分布
    pub async fn get_employee_overview(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<EmployeeOverview, DbErr> {
        Ok(EmployeeOverview {
            total_employees: self.get_total_employees(company_id, date_range).await?,
            department_distribution: self
                .get_department_distribution(company_id, date_range)
                .await?,
            gender_distribution: self.get_gender_distribution(company_id, date_range).await?,
            age_distribution: self.get_age_distribution(company_id, date_range).await?,
        })
    }

    /// 获取招聘概况统计
    ///
    /// 包含：
    /// - 候选人状态分布
    /// - 本月面试数量
    /// - 面试转化率
    /// - 部门招聘需求TOP5
    pub async fn get_recruitment_stats(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<RecruitmentStats, DbErr> {
        Ok(RecruitmentStats {
            candidate_status_distribution: self
                .get_candidate_status_distribution(company_id, date_range)
                .await?,
            monthly_interviews: self.get_monthly_interviews(company_id, date_range).await?,
            conversion_rate: self.get_conversion_rate(company_id, date_range).await?,
            department_recruitment_top5: self
                .get_department_recruitment_top5(company_id, date_range)
                .await?,
        })
    }

    /// 获取组织发展统计
    ///
    /// 包含：
    /// - 员工增长趋势（近12个月）
    /// - 部门人员变化趋势
    /// - 职位分布
    /// - 入职时长分布
    pub async fn get_organization_stats(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<OrganizationStats, DbErr> {
        Ok(OrganizationStats {
            employee_growth_trend: self
                .get_employee_growth_trend(company_id, date_range)
                .await?,
            department_growth_trend: self
                .get_department_growth_trend(company_id, date_range)
                .await?,
            position_distribution: self
                .get_position_distribution(company_id, date_range)
                .await?,
            tenure_distribution: self.get_tenure_distribution(company_id, date_range).await?,
        })
    }

    /// 获取完整的看板统计数据
    pub async fn get_stats(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<DashboardStats, DbErr> {
        let employee_overview = self.get_employee_overview(company_id, date_range).await?;
        let recruitment_stats = self.get_recruitment_stats(company_id, date_range).await?;
        let organization_stats = self.get_organization_stats(company_id, date_range).await?;

        Ok(DashboardStats {
            total_employees: employee_overview.total_employees,
            department_distribution: employee_overview.department_distribution,
            gender_distribution: employee_overview.gender_distribution,
            age_distribution: employee_overview.age_distribution,
            candidate_status_distribution: recruitment_stats.candidate_status_distribution,
            monthly_interviews: recruitment_stats.monthly_interviews,
            conversion_rate: recruitment_stats.conversion_rate,
            department_recruitment_top5: recruitment_stats.department_recruitment_top5,
            employee_growth_trend: organization_stats.employee_growth_trend,
            department_growth_trend: organization_stats.department_growth_trend,
            position_distribution: organization_stats.position_distribution,
            tenure_distribution: organization_stats.tenure_distribution,
        })
    }

    /// 获取指定时间范围内过生日的员工列表
    pub async fn get_birthday_employees(
        &self,
        company_id: i32,
        date_range: &DateRange,
    ) -> Result<Vec<BirthdayEmployee>, DbErr> {
        // 先获取所有员工
        let employees = Employee::find()
            .find_also_related(EmployeePosition)
            .filter(employee_position::Column::CompanyId.eq(company_id))
            .filter(employee::Column::Birthdate.is_not_null())
            .order_by_asc(employee::Column::Birthdate)
            .all(&self.db)
            .await?;

        let mut result = Vec::new();
        for (emp, emp_pos) in employees {
            if let Some(emp_pos) = emp_pos {
                // 获取部门和职位信息
                let dept = Department::find_by_id(emp_pos.department_id)
                    .one(&self.db)
                    .await?;
                let pos = Position::find_by_id(emp_pos.position_id)
                    .one(&self.db)
                    .await?;

                if let (Some(dept), Some(pos)) = (dept, pos) {
                    // 检查生日是否在指定范围内
                    let birthdate = emp.birthdate.unwrap();
                    let birth_month_day = (birthdate.month(), birthdate.day());
                    let start_month_day =
                        (date_range.start_time.month(), date_range.start_time.day());
                    let end_month_day = (date_range.end_time.month(), date_range.end_time.day());

                    // 处理跨年的情况
                    let is_in_range = if start_month_day <= end_month_day {
                        // 普通情况：例如 2月1日 到 2月28日
                        birth_month_day >= start_month_day && birth_month_day <= end_month_day
                    } else {
                        // 跨年情况：例如 12月1日 到 1月31日
                        birth_month_day >= start_month_day || birth_month_day <= end_month_day
                    };

                    if is_in_range {
                        result.push(BirthdayEmployee {
                            id: emp.id,
                            name: emp.name,
                            department: dept.name,
                            position: pos.name,
                            birthdate,
                        });
                    }
                }
            }
        }

        // 按月日排序
        result.sort_by_key(|emp| (emp.birthdate.month(), emp.birthdate.day()));
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_runner;
    use chrono::{Duration, Local};

    /// 创建测试服务实例
    async fn setup_test_service() -> DashboardService {
        let db = test_runner::setup_database().await;
        DashboardService::new(db)
    }

    /// 测试获取看板统计数据
    #[tokio::test]
    async fn test_get_dashboard_stats() {
        let service = setup_test_service().await;
        let now = Local::now().naive_local();
        let date_range = DateRange {
            start_time: now - Duration::days(30),
            end_time: now,
        };
        let result = service.get_stats(1, &date_range).await;
        assert!(result.is_ok(), "获取看板统计数据失败: {:?}", result.err());

        let stats = result.unwrap();
        assert!(stats.total_employees >= 0);
        assert!(stats.monthly_interviews >= 0);
        assert!(stats.conversion_rate >= 0.0 && stats.conversion_rate <= 1.0);
    }
}
