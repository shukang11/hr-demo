use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

/// 用户模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct User {
    /// 用户唯一标识符
    pub id: Uuid,
    /// 用户名
    pub username: String,
    /// 电子邮箱
    pub email: String,
    /// 密码哈希值
    pub password_hash: String,
    /// 用户全名
    pub full_name: String,
    /// 所属部门ID
    pub department_id: Option<Uuid>,
    /// 是否激活
    pub is_active: bool,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

impl Model for User {
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

/// 创建用户的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateUser {
    /// 用户名
    pub username: String,
    /// 电子邮箱
    pub email: String,
    /// 密码（明文）
    pub password: String,
    /// 用户全名
    pub full_name: String,
    /// 所属部门ID
    pub department_id: Option<Uuid>,
}

/// 更新用户的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateUser {
    /// 电子邮箱
    pub email: Option<String>,
    /// 用户全名
    pub full_name: Option<String>,
    /// 所属部门ID
    pub department_id: Option<Uuid>,
    /// 是否激活
    pub is_active: Option<bool>,
}