use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

/// JSON Schema模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct JsonSchema {
    /// 唯一标识符
    pub id: Uuid,
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

impl Model for JsonSchema {
    fn id(&self) -> Uuid {
        self.id
    }

    fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }

    fn updated_at(&self) -> DateTime<Utc> {
        self.updated_at
    }
}

/// 创建JSON Schema的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateJsonSchema {
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
}

/// 更新JSON Schema的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateJsonSchema {
    /// Schema名称
    pub name: Option<String>,
    /// Schema定义（JSON）
    pub schema: Option<Value>,
} 