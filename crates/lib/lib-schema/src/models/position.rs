use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

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

impl Model for Position {
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

/// 创建职位的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreatePosition {
    /// 职位名称
    pub name: String,
    /// 所属公司ID
    pub company_id: Uuid,
    /// 备注
    pub remark: Option<String>,
}

/// 更新职位的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdatePosition {
    /// 职位名称
    pub name: Option<String>,
    /// 备注
    pub remark: Option<String>,
} 