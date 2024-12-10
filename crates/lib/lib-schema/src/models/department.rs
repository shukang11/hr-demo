use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;

use sea_orm::FromQueryResult;

/// 部门模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Department {
    /// 部门唯一标识符
    pub id: Uuid,
    /// 部门名称
    pub name: String,
    /// 父部门ID
    pub parent_id: Option<Uuid>,
    /// 所属公司ID
    pub company_id: Uuid,
    /// 部门负责人ID
    pub leader_id: Option<Uuid>,
    /// 备注
    pub remark: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 部门数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct InsertDepartment {
    /// 部门唯一标识符（更新时使用）
    pub id: Option<Uuid>,
    /// 部门名称
    pub name: String,
    /// 父部门ID
    pub parent_id: Option<Uuid>,
    /// 所属公司ID
    pub company_id: Uuid,
    /// 部门负责人ID
    pub leader_id: Option<Uuid>,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for Department {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        Ok(Self {
            id: Uuid::from_u128(res.try_get::<i32>(pre, "id")? as u128),
            name: res.try_get(pre, "name")?,
            parent_id: res.try_get::<i32>(pre, "parent_id")
                .ok()
                .map(|id| Uuid::from_u128(id as u128)),
            company_id: Uuid::from_u128(res.try_get::<i32>(pre, "company_id")? as u128),
            leader_id: res.try_get::<i32>(pre, "leader_id")
                .ok()
                .map(|id| Uuid::from_u128(id as u128)),
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
