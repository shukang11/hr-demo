use chrono::NaiveDateTime;
use lib_entity::{
    candidate,
    entities::candidate::{CandidateStatus, Entity as Candidate},
};
use lib_schema::models::candidate::{
    Candidate as SchemaCandidate, InsertCandidate, UpdateCandidateStatus,
};
use sea_orm::*;

#[derive(Clone)]
pub struct CandidateService {
    db: DatabaseConnection,
}

impl CandidateService {
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 检查同一天内是否存在重复的候选人
    async fn check_duplicate(
        &self,
        company_id: i32,
        name: &str,
        phone: &Option<String>,
        email: &Option<String>,
        interview_date: &Option<NaiveDateTime>,
    ) -> Result<bool, DbErr> {
        use chrono::Timelike;
        use sea_orm::QueryFilter;

        let interview_date = interview_date.unwrap_or_else(|| chrono::Utc::now().naive_utc());
        let start_of_day = interview_date
            .with_hour(0)
            .unwrap()
            .with_minute(0)
            .unwrap()
            .with_second(0)
            .unwrap()
            .with_nanosecond(0)
            .unwrap();
        let end_of_day = interview_date
            .with_hour(23)
            .unwrap()
            .with_minute(59)
            .unwrap()
            .with_second(59)
            .unwrap()
            .with_nanosecond(999999999)
            .unwrap();

        let mut query = Candidate::find()
            .filter(candidate::Column::CompanyId.eq(company_id))
            .filter(candidate::Column::Name.eq(name))
            .filter(candidate::Column::InterviewDate.between(start_of_day, end_of_day));

        // 如果提供了手机号，加入手机号匹配条件
        if let Some(phone) = phone {
            query = query.filter(candidate::Column::Phone.eq(phone));
        }

        // 如果提供了邮箱，加入邮箱匹配条件
        if let Some(email) = email {
            query = query.filter(candidate::Column::Email.eq(email));
        }

        let count = query.count(&self.db).await?;
        Ok(count > 0)
    }

    /// 创建候选人
    pub async fn create(&self, params: InsertCandidate) -> Result<SchemaCandidate, DbErr> {
        // 检查是否存在重复候选人
        if self
            .check_duplicate(
                params.company_id,
                &params.name,
                &params.phone,
                &params.email,
                &params.interview_date,
            )
            .await?
        {
            return Err(DbErr::Custom("同一天内已存在相同姓名的候选人".to_string()));
        }

        let candidate = candidate::ActiveModel {
            company_id: Set(params.company_id),
            name: Set(params.name),
            phone: Set(params.phone),
            email: Set(params.email),
            position_id: Set(params.position_id),
            department_id: Set(params.department_id),
            interview_date: Set(params
                .interview_date
                .unwrap_or_else(|| chrono::Utc::now().naive_utc())),
            status: Set(CandidateStatus::Pending),
            interviewer_id: Set(params.interviewer_id),
            evaluation: Set(None),
            remark: Set(None),
            extra_value: Set(params.extra_value),
            extra_schema_id: Set(params.extra_schema_id),
            ..Default::default()
        };

        let result = candidate.insert(&self.db).await?;
        Ok(result.into())
    }

    /// 更新候选人状态
    pub async fn update_status(
        &self,
        id: i32,
        status_update: UpdateCandidateStatus,
    ) -> Result<SchemaCandidate, DbErr> {
        let candidate = Candidate::find_by_id(id)
            .one(&self.db)
            .await?
            .ok_or(DbErr::Custom("Candidate not found".to_string()))?;

        let mut candidate: candidate::ActiveModel = candidate.into();
        candidate.status = Set(status_update.status);
        candidate.evaluation = Set(status_update.evaluation);
        candidate.remark = Set(status_update.remark);

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
