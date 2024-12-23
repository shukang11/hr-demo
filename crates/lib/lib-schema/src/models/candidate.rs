use chrono::NaiveDateTime;
use lib_entity::candidate::Model as DbCandidate;
use sea_orm::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use sea_orm::FromQueryResult;

/// 候选人模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Candidate {
    /// 唯一标识符
    pub id: i32,
    /// 公司ID
    pub company_id: i32,
    /// 候选人姓名
    pub name: String,
    /// 联系电话
    pub phone: Option<String>,
    /// 电子邮箱
    pub email: Option<String>,
    /// 应聘职位ID
    pub position_id: i32,
    /// 目标部门ID
    pub department_id: i32,
    /// 面试日期
    pub interview_date: NaiveDateTime,
    /// 状态
    pub status: Option<String>,
    /// 面试官ID
    pub interviewer_id: Option<i32>,
    /// 面试评价
    pub evaluation: Option<String>,
    /// 备注
    pub remark: Option<String>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<i32>,
    /// 创建时间
    pub created_at: NaiveDateTime,
    /// 更新时间
    pub updated_at: NaiveDateTime,
}

/// 候选人数模型，用于创建和更新
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InsertCandidate {
    /// 唯一标识符（更新时使用）
    pub id: Option<i32>,
    /// 公司ID
    pub company_id: i32,
    /// 候选人姓名
    pub name: String,
    /// 联系电话
    pub phone: Option<String>,
    /// 电子邮箱
    pub email: Option<String>,
    /// 应聘职位ID
    pub position_id: i32,
    /// 目标部门ID
    pub department_id: i32,
    /// 面试日期
    pub interview_date: NaiveDateTime,
    /// 面试官ID
    pub interviewer_id: Option<i32>,
    /// 额外字段值（JSON）
    pub extra_value: Option<Value>,
    /// 额外字段模式ID
    pub extra_schema_id: Option<i32>,
}

/// 更新候选人状态的请求模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateCandidateStatus {
    /// 状态
    pub status: String,
    /// 面试评价
    pub evaluation: Option<String>,
    /// 备注
    pub remark: Option<String>,
}

impl FromQueryResult for Candidate {
    fn from_query_result(res: &QueryResult, pre: &str) -> Result<Self, DbErr> {
        let extra_value: Option<Value> = res
            .try_get::<String>(pre, "extra_value")
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok());

        Ok(Self {
            id: res.try_get(pre, "id")?,
            company_id: res.try_get(pre, "company_id")?,
            name: res.try_get(pre, "name")?,
            phone: res.try_get(pre, "phone")?,
            email: res.try_get(pre, "email").unwrap_or(None),
            position_id: res.try_get(pre, "position_id")?,
            department_id: res.try_get(pre, "department_id")?,
            interview_date: res.try_get(pre, "interview_date")?,
            status: res.try_get(pre, "status")?,
            interviewer_id: res.try_get(pre, "interviewer_id")?,
            evaluation: res.try_get(pre, "evaluation").unwrap_or(None),
            remark: res.try_get(pre, "remark").unwrap_or(None),
            extra_value,
            extra_schema_id: res.try_get(pre, "extra_schema_id").ok(),
            created_at: res.try_get(pre, "created_at")?,
            updated_at: res.try_get(pre, "updated_at")?,
        })
    }
}

impl From<DbCandidate> for Candidate {
    fn from(model: DbCandidate) -> Self {
        Self {
            id: model.id,
            company_id: model.company_id,
            name: model.name,
            phone: model.phone,
            email: model.email,
            position_id: model.position_id,
            department_id: model.department_id,
            interview_date: model.interview_date,
            status: model.status,
            interviewer_id: model.interviewer_id,
            evaluation: model.evaluation,
            remark: model.remark,
            extra_value: model.extra_value,
            extra_schema_id: model.extra_schema_id,
            created_at: model.created_at,
            updated_at: model.updated_at,
        }
    }
} 