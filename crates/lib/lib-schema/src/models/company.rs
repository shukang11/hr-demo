use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use utoipa::ToSchema;

use sea_orm::FromQueryResult;

/// 公司模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Company {
    /// 公司唯一标识符
    pub id: Uuid,
    /// 公司名称
    pub name: String,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 公司数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct InsertCompany {
    /// 公司唯一标识符（更新时使用）
    pub id: Option<Uuid>,
    /// 公司名称
    pub name: String,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
}

impl FromQueryResult for Company {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        let extra_value: Option<Value> = if let Ok(json_str) = res.try_get::<String>(pre, "extra_value") {
            serde_json::from_str(&json_str).unwrap_or(None)
        } else {
            None
        };

        Ok(Self {
            id: Uuid::from_u128(res.try_get::<i32>(pre, "id")? as u128),
            name: res.try_get(pre, "name")?,
            extra_value,
            extra_schema_id: res.try_get::<i32>(pre, "extra_schema_id")
                .ok()
                .map(|id| Uuid::from_u128(id as u128)),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}