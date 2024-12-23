use chrono::naive::serde::ts_milliseconds_option::serialize as to_milli_tsopt;
use chrono::NaiveDateTime;
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use super::{company, department, employee, json_schema, position};

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct Entity;

impl EntityName for Entity {
    fn table_name(&self) -> &str {
        "candidates"
    }
    fn schema_name(&self) -> Option<&str> {
        None
    }
}

#[derive(Clone, Debug, PartialEq, DeriveModel, DeriveActiveModel, Deserialize, Serialize)]
pub struct Model {
    #[serde(skip)]
    pub id: i32,                          // 主键
    pub company_id: i32,                  // 公司ID
    pub name: String,                     // 候选人姓名
    pub phone: Option<String>,            // 联系电话
    pub email: Option<String>,            // 电子邮箱
    pub position_id: i32,                 // 应聘职位ID
    pub department_id: i32,               // 目标部门ID
    pub interview_date: NaiveDateTime,    // 面试日期
    pub status: Option<String>,           // 状态
    pub interviewer_id: Option<i32>,      // 面试官ID
    pub evaluation: Option<String>,       // 面试评价
    pub remark: Option<String>,           // 备注
    pub extra_value: Option<Value>,       // 额外JSON数据
    pub extra_schema_id: Option<i32>,     // 额外数据schema ID
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub created_at: NaiveDateTime,        // 创建时间
    #[serde(skip)]
    #[serde(serialize_with = "to_milli_tsopt")]
    pub updated_at: NaiveDateTime,        // 更新时间
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum Column {
    Id,
    CompanyId,
    Name,
    Phone,
    Email,
    PositionId,
    DepartmentId,
    InterviewDate,
    Status,
    InterviewerId,
    Evaluation,
    Remark,
    ExtraValue,
    ExtraSchemaId,
    CreatedAt,
    UpdatedAt,
}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKey {
    Id,
}

impl PrimaryKeyTrait for PrimaryKey {
    type ValueType = i32;
    fn auto_increment() -> bool {
        true
    }
}

impl ColumnTrait for Column {
    type EntityName = Entity;
    fn def(&self) -> ColumnDef {
        match self {
            Self::Id => ColumnType::Integer.def(),
            Self::CompanyId => ColumnType::Integer.def(),
            Self::Name => ColumnType::String(StringLen::N(64)).def(),
            Self::Phone => ColumnType::String(StringLen::N(20)).def(),
            Self::Email => ColumnType::String(StringLen::N(255)).def().null(),
            Self::PositionId => ColumnType::Integer.def(),
            Self::DepartmentId => ColumnType::Integer.def(),
            Self::InterviewDate => ColumnType::DateTime.def(),
            Self::Status => ColumnType::String(StringLen::N(20)).def(),
            Self::InterviewerId => ColumnType::Integer.def(),
            Self::Evaluation => ColumnType::Text.def().null(),
            Self::Remark => ColumnType::String(StringLen::N(255)).def().null(),
            Self::ExtraValue => ColumnType::Json.def().null(),
            Self::ExtraSchemaId => ColumnType::Integer.def().null(),
            Self::CreatedAt => ColumnType::DateTime
                .def()
                .default(Expr::current_timestamp()),
            Self::UpdatedAt => ColumnType::DateTime
                .def()
                .default(Expr::current_timestamp()),
        }
    }
}

#[derive(Copy, Clone, Debug, EnumIter)]
pub enum Relation {
    Company,
    Position,
    Department,
    Interviewer,
    ExtraSchema,
}

impl RelationTrait for Relation {
    fn def(&self) -> RelationDef {
        match self {
            Self::Company => Entity::belongs_to(company::Entity)
                .from(Column::CompanyId)
                .to(company::Column::Id)
                .into(),
            Self::Position => Entity::belongs_to(position::Entity)
                .from(Column::PositionId)
                .to(position::Column::Id)
                .into(),
            Self::Department => Entity::belongs_to(department::Entity)
                .from(Column::DepartmentId)
                .to(department::Column::Id)
                .into(),
            Self::Interviewer => Entity::belongs_to(employee::Entity)
                .from(Column::InterviewerId)
                .to(employee::Column::Id)
                .into(),
            Self::ExtraSchema => Entity::belongs_to(json_schema::Entity)
                .from(Column::ExtraSchemaId)
                .to(json_schema::Column::Id)
                .into(),
        }
    }
}

impl ActiveModelBehavior for ActiveModel {} 