use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// 基础模型特征
pub trait Model {
    fn id(&self) -> Uuid;
    fn created_at(&self) -> DateTime<Utc>;
    fn updated_at(&self) -> DateTime<Utc>;
}

/// 通用的模型字段
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BaseFields {
    pub id: Uuid,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl BaseFields {
    pub fn new() -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            created_at: now,
            updated_at: now,
        }
    }
}

impl Default for BaseFields {
    fn default() -> Self {
        Self::new()
    }
}