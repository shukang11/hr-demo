use chrono::{DateTime, Utc};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;

use sea_orm::FromQueryResult;

/// JSON Schema模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonSchema {
    /// 唯一标识符
    pub id: i32,
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 创建JSON Schema的请求数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateJsonSchema {
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
}

/// 更新JSON Schema的请求数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateJsonSchema {
    /// Schema名称
    pub name: Option<String>,
    /// Schema定义（JSON）
    pub schema: Option<Value>,
}

impl FromQueryResult for JsonSchema {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        let schema: Value = if let Ok(json_str) = res.try_get::<String>(pre, "schema") {
            serde_json::from_str(&json_str).map_err(|e| DbErr::Custom(format!("JSON parse error: {}", e)))?
        } else {
            Value::Null
        };

        Ok(Self {
            id: res.try_get(pre, "id")?,
            name: res.try_get(pre, "name")?,
            schema,
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}