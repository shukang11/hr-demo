use chrono::NaiveDateTime;
use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::naive::serde::ts_milliseconds_option::deserialize as from_milli_tsopt;
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use sea_orm::FromQueryResult;

/// JSON Schema模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonSchema {
    /// 唯一标识符
    pub id: i32,
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
    /// 公司ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub company_id: Option<i32>,
    /// 实体类型
    pub entity_type: String,
    /// 是否系统预设Schema
    pub is_system: bool,
    /// Schema版本号
    pub version: i32,
    /// 父Schema ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_schema_id: Option<i32>,
    /// UI相关配置
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ui_schema: Option<Value>,
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
    
    // 关联数据
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_schema: Option<Box<JsonSchema>>,
}

/// 创建或更新JSON Schema的数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertJsonSchema {
    /// ID（更新时使用）
    pub id: Option<i32>,
    /// Schema名称
    pub name: String,
    /// Schema定义（JSON）
    pub schema: Value,
    /// 公司ID
    pub company_id: Option<i32>,
    /// 实体类型
    pub entity_type: String,
    /// 是否系统预设Schema
    pub is_system: Option<bool>,
    /// 父Schema ID
    pub parent_schema_id: Option<i32>,
    /// UI相关配置
    pub ui_schema: Option<Value>,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for JsonSchema {
    fn from_query_result(
        res: &QueryResult,
        pre: &str,
    ) -> Result<Self, DbErr> {
        let schema: Value = if let Ok(json_str) = res.try_get::<String>(pre, "schema") {
            serde_json::from_str(&json_str).map_err(|e| DbErr::Custom(format!("JSON parse error: {}", e)))?
        } else {
            Value::Null
        };

        let ui_schema: Option<Value> = if let Ok(json_str) = res.try_get::<String>(pre, "ui_schema") {
            if json_str.is_empty() {
                None
            } else {
                serde_json::from_str(&json_str)
                    .map(Some)
                    .map_err(|e| DbErr::Custom(format!("UI Schema JSON parse error: {}", e)))?
            }
        } else {
            None
        };

        Ok(Self {
            id: res.try_get(pre, "id")?,
            name: res.try_get(pre, "name")?,
            schema,
            company_id: res.try_get(pre, "company_id").ok(),
            entity_type: res.try_get(pre, "entity_type").unwrap_or_else(|_| "GENERAL".to_string()),
            is_system: res.try_get(pre, "is_system").unwrap_or(false),
            version: res.try_get(pre, "version").unwrap_or(1),
            parent_schema_id: res.try_get(pre, "parent_schema_id").ok(),
            ui_schema,
            remark: res.try_get(pre, "remark").ok(),
            created_at: Some(res.try_get(pre, "created_at")?),
            updated_at: Some(res.try_get(pre, "updated_at").unwrap_or_else(|_| res.try_get(pre, "created_at").unwrap())),
            parent_schema: None,
        })
    }
}

impl From<lib_entity::json_schema::Model> for JsonSchema {
    fn from(value: lib_entity::json_schema::Model) -> Self {
        Self {
            id: value.id,
            name: value.name, 
            schema: value.schema,
            company_id: value.company_id,
            entity_type: "GENERAL".to_string(), // 默认值，因为旧模型中没有这个字段
            is_system: false,                  // 默认值
            version: 1,                        // 默认版本号
            parent_schema_id: None,            // 旧模型中没有这个字段
            ui_schema: None,                   // 旧模型中没有这个字段
            remark: value.remark,
            created_at: Some(value.created_at),
            updated_at: Some(value.created_at), // 旧模型中没有updated_at，使用created_at代替
            parent_schema: None,
        }
    }
}