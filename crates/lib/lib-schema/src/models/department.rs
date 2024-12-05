use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::Model;

/// 部门模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Department {
    pub id: Uuid,
    pub name: String,
    pub description: Option<String>,
    pub parent_id: Option<Uuid>,
    pub created_at: DateTime<Utc>,
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
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateDepartment {
    pub name: String,
    pub description: Option<String>,
    pub parent_id: Option<Uuid>,
}

/// 更新部门的请求数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateDepartment {
    pub name: Option<String>,
    pub description: Option<String>,
    pub parent_id: Option<Uuid>,
}