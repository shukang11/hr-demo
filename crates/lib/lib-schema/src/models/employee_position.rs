use chrono::naive::serde::ts_milliseconds::deserialize as from_milli_ts;
use chrono::naive::serde::ts_milliseconds::serialize as to_milli_ts;
use chrono::naive::serde::ts_milliseconds_option::deserialize as from_milli_tsopt;
use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use lib_entity::entities::employee_position::Model as DbEmployeePosition;
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};

use sea_orm::FromQueryResult;

/// 员工职位关联模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmployeePosition {
    /// 唯一标识符
    pub id: i32,
    /// 员工ID
    pub employee_id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 部门ID
    pub department_id: i32,
    /// 职位ID
    pub position_id: i32,
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
    /// 入职时间
    #[serde(serialize_with = "to_milli_ts", deserialize_with = "from_milli_ts")]
    pub entry_at: NaiveDateTime,
}

/// 员工职位关联数据模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertEmployeePosition {
    /// 唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 员工ID
    pub employee_id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 部门ID
    pub department_id: i32,
    /// 职位ID
    pub position_id: i32,
    /// 入职时间
    #[serde(serialize_with = "to_milli_ts", deserialize_with = "from_milli_ts")]
    pub entry_at: NaiveDateTime,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for EmployeePosition {
    fn from_query_result(res: &QueryResult, pre: &str) -> Result<Self, DbErr> {
        Ok(Self {
            id: res.try_get(pre, "id")?,
            employee_id: res.try_get(pre, "employee_id")?,
            company_id: res.try_get(pre, "company_id")?,
            department_id: res.try_get(pre, "department_id")?,
            position_id: res.try_get(pre, "position_id")?,
            remark: res.try_get(pre, "remark").unwrap_or(None),
            created_at: Some(res.try_get(pre, "created_at")?),
            updated_at: Some(res.try_get(pre, "updated_at")?),
            entry_at: res.try_get(pre, "entry_at")?,
        })
    }
}

impl From<DbEmployeePosition> for EmployeePosition {
    fn from(model: DbEmployeePosition) -> Self {
        Self {
            id: model.id,
            employee_id: model.employee_id,
            company_id: model.company_id,
            department_id: model.department_id,
            position_id: model.position_id,
            remark: model.remark,
            created_at: Some(model.created_at),
            updated_at: Some(model.updated_at),
            entry_at: model.entry_at,
        }
    }
}
