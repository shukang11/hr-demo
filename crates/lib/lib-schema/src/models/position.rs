use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use lib_entity::entities::position::Model;

use sea_orm::FromQueryResult;

/// 职位模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    /// 职位唯一标识符
    pub id: i32,
    /// 职位名称
    pub name: String,
    /// 所属公司ID
    pub company_id: i32,
    /// 备注
    pub remark: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 职位数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertPosition {
    /// 职位唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 职位名称
    pub name: String,
    /// 所属公司ID
    pub company_id: i32,
    /// 备注
    pub remark: Option<String>,
}

impl From<Model> for Position {
    fn from(model: Model) -> Self {
        Self {
            id: model.id,
            name: model.name,
            company_id: model.company_id,
            remark: model.remark,
            created_at: model.created_at.and_utc(),
            updated_at: model.updated_at.and_utc(),
        }
    }
}

impl FromQueryResult for Position {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        Ok(Self {
            id: res.try_get(pre, "id")?,
            name: res.try_get(pre, "name")?,
            company_id: res.try_get(pre, "company_id")?,
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
