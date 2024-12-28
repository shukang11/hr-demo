use sea_orm::*;
use chrono::NaiveDateTime;
use lib_entity::{candidate, entities::candidate::Entity as Candidate};
use lib_schema::models::candidate::Candidate as SchemaCandidate;

#[derive(Clone)]
pub struct CandidateService {
    db: DatabaseConnection,
}

impl CandidateService {
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 创建候选人
    pub async fn create(
        &self,
        company_id: i32,
        name: String,
        phone: Option<String>,
        email: Option<String>,
        position_id: i32,
        department_id: i32,
        interview_date: Option<NaiveDateTime>,
        interviewer_id: Option<i32>,
        extra_value: Option<serde_json::Value>,
        extra_schema_id: Option<i32>,
    ) -> Result<SchemaCandidate, DbErr> {
        let candidate = candidate::ActiveModel {
            company_id: Set(company_id),
            name: Set(name),
            phone: Set(phone),
            email: Set(email),
            position_id: Set(position_id),
            department_id: Set(department_id),
            interview_date: Set(interview_date.unwrap_or_else(|| chrono::Utc::now().naive_utc())),
            status: Set(Some("待面试".to_string())),
            interviewer_id: Set(interviewer_id),
            evaluation: Set(None),
            remark: Set(None),
            extra_value: Set(extra_value),
            extra_schema_id: Set(extra_schema_id),
            ..Default::default()
        };

        let result = candidate.insert(&self.db).await?;
        Ok(result.into())
    }

    /// 更新候选人状态
    pub async fn update_status(
        &self,
        id: i32,
        status: String,
        evaluation: Option<String>,
        remark: Option<String>,
    ) -> Result<SchemaCandidate, DbErr> {
        let candidate = Candidate::find_by_id(id)
            .one(&self.db)
            .await?
            .ok_or(DbErr::Custom("Candidate not found".to_string()))?;

        let mut candidate: candidate::ActiveModel = candidate.into();
        candidate.status = Set(Some(status));
        candidate.evaluation = Set(evaluation);
        candidate.remark = Set(remark);

        let result = candidate.update(&self.db).await?;
        Ok(result.into())
    }

    /// 获取候选人列表
    pub async fn find_all(&self, company_id: i32) -> Result<Vec<SchemaCandidate>, DbErr> {
        let results = Candidate::find()
            .filter(candidate::Column::CompanyId.eq(company_id))
            .order_by_desc(candidate::Column::CreatedAt)
            .all(&self.db)
            .await?;
        
        Ok(results.into_iter().map(|model| model.into()).collect())
    }

    /// 获取候选人详情
    pub async fn find_by_id(&self, id: i32) -> Result<Option<SchemaCandidate>, DbErr> {
        let result = Candidate::find_by_id(id).one(&self.db).await?;
        Ok(result.map(|model| model.into()))
    }

    /// 删除候选人
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        Candidate::delete_by_id(id).exec(&self.db).await
    }
} 