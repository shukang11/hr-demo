use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;
use sea_orm::FromQueryResult;

/// 职位模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Position {
    /// 职位唯一标识符
    pub id: Uuid,
    /// 职位名称
    pub name: String,
    /// 所属公司ID
    pub company_id: Uuid,
    /// 备注
    pub remark: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 职位数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct InsertPosition {
    /// 职位唯一标识符（更新时使用）
    pub id: Option<Uuid>,
    /// 职位名称
    pub name: String,
    /// 所属公司ID
    pub company_id: Uuid,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for Position {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        Ok(Self {
            id: Uuid::from_u128(res.try_get::<i32>(pre, "id")? as u128),
            name: res.try_get(pre, "name")?,
            company_id: Uuid::from_u128(res.try_get::<i32>(pre, "company_id")? as u128),
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
