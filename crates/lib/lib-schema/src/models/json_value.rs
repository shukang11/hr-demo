use chrono::naive::serde::ts_milliseconds_option::deserialize as from_milli_tsopt;
use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::FromQueryResult;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// JSON Value 领域模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonValue {
    /// 主键
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<i32>,
    /// 关联的JSON Schema ID
    pub schema_id: i32,
    /// 关联的实体ID
    pub entity_id: i32,
    /// 关联的实体类型
    pub entity_type: String,
    /// 实际存储的JSON数据
    pub value: Value,
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

/// 新增或更新 JsonValue 用的数据结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertJsonValue {
    /// 主键（更新时用）
    pub id: Option<i32>,
    pub schema_id: i32,
    pub entity_id: i32,
    pub entity_type: String,
    pub value: Value,
    pub remark: Option<String>,
}

/// 查询实体的所有 JSON 值时用的数据结构
#[derive(Debug, Clone, Serialize, Deserialize, FromQueryResult)]
pub struct QueryEntityValues {
    pub schema_id: i32,
    pub entity_id: i32,
    pub entity_type: String,
    pub value: Value,
    pub remark: Option<String>,
}

impl FromQueryResult for JsonValue {
    fn from_query_result(res: &sea_orm::QueryResult, pre: &str) -> Result<Self, sea_orm::DbErr> {
        Ok(Self {
            id: res.try_get(pre, "id")?,
            schema_id: res.try_get(pre, "schema_id")?,
            entity_id: res.try_get(pre, "entity_id")?,
            entity_type: res.try_get(pre, "entity_type")?,
            value: res.try_get(pre, "value")?,
            remark: res.try_get(pre, "remark").ok(),
            created_at: Some(res.try_get(pre, "created_at")?),
            updated_at: Some(
                res.try_get(pre, "updated_at")
                    .unwrap_or_else(|_| res.try_get(pre, "created_at").unwrap()),
            ),
        })
    }
}

impl From<lib_entity::json_value::Model> for JsonValue {
    fn from(model: lib_entity::json_value::Model) -> Self {
        Self {
            id: Some(model.id),
            schema_id: model.schema_id,
            entity_id: model.entity_id,
            entity_type: model.entity_type,
            value: model.value,
            remark: model.remark,
            created_at: Some(model.created_at),
            updated_at: Some(model.updated_at),
        }
    }
}
