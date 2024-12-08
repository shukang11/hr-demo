use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use utoipa::ToSchema;
use sea_orm::prelude::*;

use sea_orm::FromQueryResult;

/// 性别枚举
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum Gender {
    /// 男性
    Male,
    /// 女性
    Female,
    /// 未知
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
    pub birthdate: Option<DateTime<Utc>>,
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
    pub birthdate: Option<DateTime<Utc>>,
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
    pub birthdate: Option<DateTime<Utc>>,
    /// 地址
    pub address: Option<String>,
    /// 性别
    pub gender: Option<Gender>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<Uuid>,
}

impl FromQueryResult for Employee {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        let extra_value: Option<Value> = if let Ok(json_str) = res.try_get::<String>(pre, "extra_value") {
            serde_json::from_str(&json_str).unwrap_or(None)
        } else {
            None
        };

        Ok(Self {
            id: Uuid::from_u128(res.try_get::<i32>(pre, "id")? as u128),
            name: res.try_get(pre, "name")?,
            email: res.try_get(pre, "email").unwrap_or(None),
            phone: res.try_get(pre, "phone").unwrap_or(None),
            birthdate: res.try_get(pre, "birthdate").unwrap_or(None),
            address: res.try_get(pre, "address").unwrap_or(None),
            gender: match res.try_get::<String>(pre, "gender")?.as_str() {
                "Male" => Gender::Male,
                "Female" => Gender::Female,
                _ => Gender::Unknown,
            },
            extra_value,
            extra_schema_id: res.try_get::<i32>(pre, "extra_schema_id")
                .ok()
                .map(|id| Uuid::from_u128(id as u128)),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}
