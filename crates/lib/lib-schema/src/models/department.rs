use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

/// 部门模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Department {
    /// 部门唯一标识符
    pub id: Uuid,
    /// 部门名称
    pub name: String,
    /// 部门描述
    pub description: Option<String>,
    /// 父部门ID
    pub parent_id: Option<Uuid>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

impl Model for Department {
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

/// 创建部门的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateDepartment {
    /// 部门名称
    pub name: String,
    /// 部门描述
    pub description: Option<String>,
    /// 父部门ID
    pub parent_id: Option<Uuid>,
}

/// 更新部门的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateDepartment {
    /// 部门名称
    pub name: Option<String>,
    /// 部门描述
    pub description: Option<String>,
    /// 父部门ID
    pub parent_id: Option<Uuid>,
}