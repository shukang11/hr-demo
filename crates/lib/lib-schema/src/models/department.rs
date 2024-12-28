use chrono::NaiveDateTime;
use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::naive::serde::ts_milliseconds_option::deserialize as from_milli_tsopt;
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use lib_entity::entities::department::Model;
use sea_orm::FromQueryResult;

/// 部门模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Department {
    /// 部门唯一标识符
    pub id: i32,
    /// 部门名称
    pub name: String,
    /// 父部门ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_id: Option<i32>,
    /// 所属公司ID
    pub company_id: i32,
    /// 部门负责人ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub leader_id: Option<i32>,
    /// 备注
    #[serde(skip_serializing_if = "Option::is_none")]
    pub remark: Option<String>,
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
}

/// 部门数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertDepartment {
    /// 部门唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 部门名称
    pub name: String,
    /// 父部门ID
    pub parent_id: Option<i32>,
    /// 所属公司ID
    pub company_id: i32,
    /// 部门负责人ID
    pub leader_id: Option<i32>,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for Department {
    fn from_query_result(res: &QueryResult, pre: &str) -> Result<Self, DbErr> {
        Ok(Self {
            id: res.try_get(pre, "id")?,
            name: res.try_get(pre, "name")?,
            parent_id: res.try_get(pre, "parent_id").ok(),
            company_id: res.try_get(pre, "company_id")?,
            leader_id: res.try_get(pre, "leader_id").ok(),
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: Some(res.try_get(pre, "created_at")?),
            updated_at: Some(res.try_get(pre, "updated_at")?),
        })
    }
}

impl From<Model> for Department {
    fn from(model: Model) -> Self {
        Self {
            id: model.id,
            name: model.name,
            parent_id: model.parent_id,
            company_id: model.company_id,
            leader_id: model.leader_id,
            remark: model.remark,
            created_at: Some(model.created_at),
            updated_at: Some(model.updated_at),
        }
    }
}
