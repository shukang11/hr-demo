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

/// 创建员工职位关联的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateEmployeePosition {
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

/// 更新员工职位关联的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateEmployeePosition {
    /// 部门ID
    pub department_id: Option<Uuid>,
    /// 职位ID
    pub position_id: Option<Uuid>,
    /// 备注
    pub remark: Option<String>,
}
