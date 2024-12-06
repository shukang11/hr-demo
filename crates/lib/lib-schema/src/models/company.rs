use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

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

impl Model for Company {
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

/// 创建公司的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateCompany {
    /// 公司名称
    pub name: String,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
}

/// 更新���司的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateCompany {
    /// 公司名称
    pub name: Option<String>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
} 