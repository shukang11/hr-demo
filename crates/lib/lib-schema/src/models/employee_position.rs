use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};

use sea_orm::FromQueryResult;

/// 员工职位关联模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmployeePosition {
    /// 唯一标识符
    pub id: i32,
    /// 员工ID
    pub employee_id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 部门ID
    pub department_id: i32,
    /// 职位ID
    pub position_id: i32,
    /// 备注
    pub remark: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 员工职位关联数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertEmployeePosition {
    /// 唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 员工ID
    pub employee_id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 部门ID
    pub department_id: i32,
    /// 职位ID
    pub position_id: i32,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for EmployeePosition {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        Ok(Self {
            id: res.try_get(pre, "id")?,
            employee_id: res.try_get(pre, "employee_id")?,
            company_id: res.try_get(pre, "company_id")?,
            department_id: res.try_get(pre, "department_id")?,
            position_id: res.try_get(pre, "position_id")?,
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
