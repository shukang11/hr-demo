use chrono::NaiveDateTime;
use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::naive::serde::ts_milliseconds_option::deserialize as from_milli_tsopt;
use lib_entity::entities::employee::{Gender as DbGender, Model as DbEmployee};
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use sea_orm::FromQueryResult;

/// 性别枚举
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Gender {
    /// 男性
    Male,
    /// 女性
    Female,
    /// 未知
    Unknown,
}

impl From<Gender> for DbGender {
    fn from(gender: Gender) -> Self {
        match gender {
            Gender::Male => DbGender::Male,
            Gender::Female => DbGender::Female,
            Gender::Unknown => DbGender::Unknown,
        }
    }
}

impl From<DbGender> for Gender {
    fn from(gender: DbGender) -> Self {
        match gender {
            DbGender::Male => Gender::Male,
            DbGender::Female => Gender::Female,
            DbGender::Unknown => Gender::Unknown,
        }
    }
}

/// 员工模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Employee {
    /// 员工唯一标识符
    pub id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 员工姓名
    pub name: String,
    /// 电子邮箱
    #[serde(skip_serializing_if = "Option::is_none")]
    pub email: Option<String>,
    /// 电话号码
    #[serde(skip_serializing_if = "Option::is_none")]
    pub phone: Option<String>,
    /// 出生日期
    #[serde(
        serialize_with = "to_milli_tsopt",
        deserialize_with = "from_milli_tsopt"
    )]
    pub birthdate: Option<NaiveDateTime>,
    /// 地址
    #[serde(skip_serializing_if = "Option::is_none")]
    pub address: Option<String>,
    /// 性别
    pub gender: Gender,
    /// 额外字段值（JSON）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extra_schema_id: Option<i32>,
    /// 创建时间
    #[serde(
        serialize_with = "to_milli_tsopt",
        deserialize_with = "from_milli_tsopt"
    )]
    pub created_at: Option<NaiveDateTime>,
    /// 更新时间
    #[serde(
        serialize_with = "to_milli_tsopt",
        deserialize_with = "from_milli_tsopt"
    )]
    pub updated_at: Option<NaiveDateTime>,
    /// 部门ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub department_id: Option<i32>,
    /// 职位ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub position_id: Option<i32>,
}

/// 员工数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertEmployee {
    /// 员工唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 公司ID
    pub company_id: i32,
    /// 员工姓名
    pub name: String,
    /// 电子邮箱
    pub email: Option<String>,
    /// 电话号码
    pub phone: Option<String>,
    /// 出生日期
    #[serde(
        serialize_with = "to_milli_tsopt",
        deserialize_with = "from_milli_tsopt"
    )]
    pub birthdate: Option<NaiveDateTime>,
    /// 地址
    pub address: Option<String>,
    /// 性别
    pub gender: Gender,
    /// 部门ID
    pub department_id: Option<i32>,
    /// 职位ID
    pub position_id: Option<i32>,
    /// 入职日期
    #[serde(
        serialize_with = "to_milli_tsopt",
        deserialize_with = "from_milli_tsopt"
    )]
    pub entry_date: Option<NaiveDateTime>,
    /// 候选人ID
    pub candidate_id: Option<i32>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<i32>,
}

impl FromQueryResult for Employee {
    fn from_query_result(res: &QueryResult, pre: &str) -> Result<Self, DbErr> {
        let extra_value: Option<Value> =
            res.try_get::<String>(pre, "extra_value")
                .ok()
                .and_then(|s| serde_json::from_str(&s).ok());

        let db_gender = match res.try_get::<String>(pre, "gender")?.as_str() {
            "Male" => DbGender::Male,
            "Female" => DbGender::Female,
            _ => DbGender::Unknown,
        };

        Ok(Self {
            id: res.try_get(pre, "id")?,
            company_id: res.try_get(pre, "company_id")?,
            name: res.try_get(pre, "name")?,
            email: res.try_get(pre, "email").unwrap_or(None),
            phone: res.try_get(pre, "phone").unwrap_or(None),
            birthdate: res.try_get(pre, "birthdate").ok(),
            address: res.try_get(pre, "address").unwrap_or(None),
            gender: db_gender.into(),
            extra_value,
            extra_schema_id: res.try_get(pre, "extra_schema_id").ok(),
            created_at: Some(res.try_get(pre, "created_at")?),
            updated_at: Some(res.try_get(pre, "updated_at")?),
            department_id: res.try_get(pre, "department_id").ok(),
            position_id: res.try_get(pre, "position_id").ok(),
        })
    }
}

impl From<DbEmployee> for Employee {
    fn from(model: DbEmployee) -> Self {
        Self {
            id: model.id,
            company_id: model.company_id,
            name: model.name,
            email: model.email,
            phone: model.phone,
            birthdate: model.birthdate,
            address: model.address,
            gender: model.gender.into(),
            extra_value: model.extra_value,
            extra_schema_id: model.extra_schema_id,
            created_at: Some(model.created_at),
            updated_at: Some(model.updated_at),
            department_id: None,
            position_id: None,
        }
    }
}
