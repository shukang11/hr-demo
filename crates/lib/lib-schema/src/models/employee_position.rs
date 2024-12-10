use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;

use sea_orm::FromQueryResult;

/// 员工职位关联模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct EmployeePosition {
    /// 唯一标识符
    pub id: Uuid,
    /// 员工ID
    pub employee_id: Uuid,
    /// 公司ID
    pub company_id: Uuid,
    /// 部门ID
    pub department_id: Uuid,
    /// 职位ID
    pub position_id: Uuid,
    /// 备注
    pub remark: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 员工职位关联数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct InsertEmployeePosition {
    /// 唯一标识符（更新时使用）
    pub id: Option<Uuid>,
    /// 员工ID
    pub employee_id: Uuid,
    /// 公司ID
    pub company_id: Uuid,
    /// 部门ID
    pub department_id: Uuid,
    /// 职位ID
    pub position_id: Uuid,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for EmployeePosition {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        Ok(Self {
            id: Uuid::from_u128(res.try_get::<i32>(pre, "id")? as u128),
            employee_id: Uuid::from_u128(res.try_get::<i32>(pre, "employee_id")? as u128),
            company_id: Uuid::from_u128(res.try_get::<i32>(pre, "company_id")? as u128),
            department_id: Uuid::from_u128(res.try_get::<i32>(pre, "department_id")? as u128),
            position_id: Uuid::from_u128(res.try_get::<i32>(pre, "position_id")? as u128),
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
