use chrono::{DateTime, NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use utoipa::ToSchema;

use super::Model;

/// 性别枚举
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum Gender {
    #[serde(rename = "Male")]
    Male,
    #[serde(rename = "Female")]
    Female,
    #[serde(rename = "Unknown")]
    Unknown,
}

/// 员工模型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Employee {
    /// 员工唯一标识符
    pub id: Uuid,
    /// 员工姓名
    pub name: String,
    /// 电子邮箱
    pub email: Option<String>,
    /// 电话号码
    pub phone: Option<String>,
    /// 出生日期
    pub birthdate: Option<NaiveDate>,
    /// 地址
    pub address: Option<String>,
    /// 性别
    pub gender: Gender,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

impl Model for Employee {
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

/// 创建员工的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CreateEmployee {
    /// 员工姓名
    pub name: String,
    /// 电子邮箱
    pub email: Option<String>,
    /// 电话号码
    pub phone: Option<String>,
    /// 出生日期
    pub birthdate: Option<NaiveDate>,
    /// 地址
    pub address: Option<String>,
    /// 性别
    pub gender: Gender,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
}

/// 更新员工的请求数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UpdateEmployee {
    /// 员工姓名
    pub name: Option<String>,
    /// 电子邮箱
    pub email: Option<String>,
    /// 电话号码
    pub phone: Option<String>,
    /// 出生日期
    pub birthdate: Option<NaiveDate>,
    /// 地址
    pub address: Option<String>,
    /// 性别
    pub gender: Option<Gender>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
} 