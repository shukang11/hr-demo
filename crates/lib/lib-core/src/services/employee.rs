use lib_entity::entities::{
    candidate::{self, CandidateStatus, Entity as Candidate},
    company, department,
    employee::{self, ActiveModel as EmployeeActive, Entity as Employee},
    employee_position::{self, ActiveModel as EmployeePositionActive, Entity as EmployeePosition},
    position,
};
use lib_schema::models::employee_position::{
    EmployeePosition as SchemaEmployeePosition, InsertEmployeePosition,
};
use lib_schema::{
    models::employee::{Employee as SchemaEmployee, InsertEmployee},
    PageParams, PageResult,
};
use sea_orm::*;

/// 员工服务
///
/// 提供员工相关的核心业务功能，包括：
/// - 创建/更新员工信息
/// - 管理员工与公司/部门/职位的关联关系
#[derive(Debug)]
pub struct EmployeeService {
    db: DatabaseConnection,
}

impl EmployeeService {
    /// 创建服务实例
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 检查员工是否重复
    async fn check_duplicate(
        &self,
        company_id: i32,
        id: Option<i32>,
        name: &str,
        phone: &Option<String>,
        email: &Option<String>,
    ) -> Result<bool, DbErr> {
        use sea_orm::QueryFilter;

        tracing::info!(
            "检查重复员工: company_id={}, id={:?}, name={}, phone={:?}, email={:?}",
            company_id,
            id,
            name,
            phone,
            email
        );

        let mut query = Employee::find()
            .filter(employee::Column::CompanyId.eq(company_id))
            .filter(employee::Column::Name.eq(name));

        // 如果是更新操作，排除当前记录
        if let Some(current_id) = id {
            query = query.filter(employee::Column::Id.ne(current_id));
        }

        // 构建手机号或邮箱的匹配条件
        let mut condition = Condition::any();

        if let Some(phone) = phone {
            if !phone.is_empty() {
                condition = condition.add(employee::Column::Phone.eq(phone.clone()));
            }
        }

        if let Some(email) = email {
            if !email.is_empty() {
                condition = condition.add(employee::Column::Email.eq(email.clone()));
            }
        }

        // 如果有手机号或邮箱条件，添加到查询中
        if condition.is_empty() {
            // 如果没有手机号和邮箱，只用名字判断
            let count = query.count(&self.db).await?;
            tracing::info!("查询结果: 找到 {} 个重名员工", count);
            Ok(count > 0)
        } else {
            // 如果有手机号或邮箱，必须同时满足名字和其他条件之一
            query = query.filter(condition);
            let count = query.count(&self.db).await?;
            tracing::info!("查询结果: 找到 {} 个重复员工", count);
            Ok(count > 0)
        }
    }

    /// 创建或更新员工
    ///
    /// # 参数
    /// - `params`: 员工参数，如果包含id则为更新，否则为创建
    ///
    /// # 返回
    /// - `Result<SchemaEmployee, DbErr>`: 成功返回员工模型，失败返回数据库错误
    pub async fn insert(&self, params: InsertEmployee) -> Result<SchemaEmployee, DbErr> {
        // 验证公司是否存在
        if !company::Entity::find_by_id(params.company_id)
            .one(&self.db)
            .await?
            .is_some()
        {
            return Err(DbErr::Custom(format!(
                "Company not found with id: {}",
                params.company_id
            )));
        }

        // 检查是否存在重复员工
        if self
            .check_duplicate(
                params.company_id,
                params.id,
                &params.name,
                &params.phone,
                &params.email,
            )
            .await?
        {
            return Err(DbErr::Custom("该公司已存在相同姓名的员工".to_string()));
        }

        // 如果提供了部门ID，验证部门是否存在且属于该公司
        if let Some(department_id) = params.department_id {
            if let Some(dept) = department::Entity::find_by_id(department_id)
                .one(&self.db)
                .await?
            {
                if dept.company_id != params.company_id {
                    return Err(DbErr::Custom(
                        "Department does not belong to the company".to_owned(),
                    ));
                }
            } else {
                return Err(DbErr::Custom("Department not found".to_owned()));
            }
        }

        // 如果提供了职位ID，验证职位是否存在且属于该公司
        if let Some(position_id) = params.position_id {
            if let Some(pos) = position::Entity::find_by_id(position_id)
                .one(&self.db)
                .await?
            {
                if pos.company_id != params.company_id {
                    return Err(DbErr::Custom(
                        "Position does not belong to the company".to_owned(),
                    ));
                }
            } else {
                return Err(DbErr::Custom("Position not found".to_owned()));
            }
        }

        // 验证候选人是否存在
        if let Some(candidate_id) = params.candidate_id {
            if !Candidate::find_by_id(candidate_id)
                .one(&self.db)
                .await?
                .is_some()
            {
                return Err(DbErr::Custom(format!(
                    "Candidate not found with id: {}",
                    candidate_id
                )));
            }
        }

        if let Some(_entry_at) = params.entry_date {
        } else {
            return Err(DbErr::Custom("entry date cant be nil".to_owned()));
        }

        let txn = self.db.begin().await?;

        let employee = match params.id {
            // 更新现有员工
            Some(id) => {
                let employee =
                    if let Some(employee) = Employee::find_by_id(id).one(&self.db).await? {
                        employee
                    } else {
                        return Err(DbErr::Custom(format!("Employee not found with id: {}", id)));
                    };

                let mut employee: EmployeeActive = employee.into();

                // 更新字段
                employee.company_id = Set(params.company_id);
                employee.name = Set(params.name);
                employee.email = Set(params.email);
                employee.phone = Set(params.phone);
                employee.birthdate = Set(params.birthdate);
                employee.address = Set(params.address);
                employee.gender = Set(params.gender.into());
                employee.extra_value = Set(params.extra_value);
                employee.extra_schema_id = Set(params.extra_schema_id);
                employee.marital_status = Set(params.marital_status.map(|s| s.into()));
                employee.emergency_contact = Set(params
                    .emergency_contact
                    .map(|c| serde_json::to_value(c).unwrap()));

                let result = employee
                    .update(&txn)
                    .await
                    .map_err(|e| DbErr::Custom(format!("Failed to update employee: {}", e)))?;

                // 如果提供了部门和职位信息，更新职位关联
                if let (Some(department_id), Some(position_id), Some(entry_at)) =
                    (params.department_id, params.position_id, params.entry_date)
                {
                    // 先删除现有的职位关联
                    EmployeePosition::delete_many()
                        .filter(employee_position::Column::EmployeeId.eq(id))
                        .exec(&txn)
                        .await?;

                    // 创建新的职位关联
                    let position = EmployeePositionActive {
                        employee_id: Set(id),
                        company_id: Set(params.company_id),
                        department_id: Set(department_id),
                        position_id: Set(position_id),
                        entry_at: Set(entry_at),
                        remark: Set(None),
                        ..Default::default()
                    };
                    position.insert(&txn).await?;
                }

                result
            }
            // 创建新员工
            None => {
                let employee = EmployeeActive {
                    company_id: Set(params.company_id),
                    name: Set(params.name),
                    email: Set(params.email),
                    phone: Set(params.phone),
                    birthdate: Set(params.birthdate),
                    address: Set(params.address),
                    gender: Set(params.gender.into()),
                    extra_value: Set(params.extra_value),
                    extra_schema_id: Set(params.extra_schema_id),
                    ..Default::default()
                };

                let result = employee
                    .insert(&txn)
                    .await
                    .map_err(|e| DbErr::Custom(format!("Failed to create employee: {}", e)))?;

                // 如果提供了部门和职位信息，创建职位关联
                if let (Some(department_id), Some(position_id), Some(entry_at)) =
                    (params.department_id, params.position_id, params.entry_date)
                {
                    let position = EmployeePositionActive {
                        employee_id: Set(result.id),
                        company_id: Set(params.company_id),
                        department_id: Set(department_id),
                        position_id: Set(position_id),
                        entry_at: Set(entry_at),
                        remark: Set(None),
                        ..Default::default()
                    };
                    position.insert(&txn).await?;
                }

                // 如果提供了候选人ID，更新候选人状态为已录用
                if let Some(candidate_id) = params.candidate_id {
                    tracing::info!(
                        "从候选人创建员工，更新候选人状态: candidate_id={}, employee_id={}",
                        candidate_id,
                        result.id
                    );

                    let candidate = Candidate::find_by_id(candidate_id)
                        .one(&txn)
                        .await?
                        .ok_or_else(|| DbErr::Custom("Candidate not found".to_owned()))?;

                    let mut candidate: candidate::ActiveModel = candidate.into();
                    candidate.status = Set(CandidateStatus::Accepted);

                    tracing::info!(
                        "更新候选人状态为已录用: candidate_id={}, new_status={:?}",
                        candidate_id,
                        CandidateStatus::Accepted
                    );

                    candidate.update(&txn).await?;

                    tracing::info!(
                        "候选人状态更新成功: candidate_id={}, employee_id={}",
                        candidate_id,
                        result.id
                    );
                }

                result
            }
        };

        txn.commit().await?;

        // 重新查询员工信息，包含职位关联
        self.find_by_id(employee.id)
            .await?
            .ok_or_else(|| DbErr::Custom("Failed to fetch employee after insert".to_owned()))
    }

    /// 删除员工
    ///
    /// # 参数
    /// - `id`: 员工ID
    ///
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        // 首先删除员工的所有职位关联
        EmployeePosition::delete_many()
            .filter(employee_position::Column::EmployeeId.eq(id))
            .exec(&self.db)
            .await?;

        // 然后删除员工
        Employee::delete_by_id(id).exec(&self.db).await
    }

    /// 根据ID查询员工
    ///
    /// # 参数
    /// - `id`: 员工ID
    ///
    /// # 返回
    /// - `Result<Option<SchemaEmployee>, DbErr>`: 成功返回员工模型（如存在），失败返回数据库错误
    pub async fn find_by_id(&self, id: i32) -> Result<Option<SchemaEmployee>, DbErr> {
        let result = Employee::find_by_id(id)
            .join(
                JoinType::LeftJoin,
                employee::Relation::EmployeePosition.def(),
            )
            .select_only()
            .column(employee::Column::Id)
            .column(employee::Column::CompanyId)
            .column(employee::Column::Name)
            .column(employee::Column::Email)
            .column(employee::Column::Phone)
            .column(employee::Column::Birthdate)
            .column(employee::Column::Address)
            .column(employee::Column::Gender)
            .column(employee::Column::ExtraValue)
            .column(employee::Column::ExtraSchemaId)
            .column(employee::Column::CreatedAt)
            .column(employee::Column::UpdatedAt)
            .column(employee_position::Column::DepartmentId)
            .column(employee_position::Column::PositionId)
            .into_model::<SchemaEmployee>()
            .one(&self.db)
            .await?;
        Ok(result)
    }

    /// 为员工添加职位
    ///
    /// # 参数
    /// - `params`: 员工职位关联参数
    ///
    /// # 返回
    /// - `Result<SchemaEmployeePosition, DbErr>`: 成功返回关联模型，失败返回数据库错误
    pub async fn add_position(
        &self,
        params: InsertEmployeePosition,
    ) -> Result<SchemaEmployeePosition, DbErr> {
        // 验证员工是否存在
        let employee_id = params.employee_id;
        if !Employee::find_by_id(employee_id)
            .one(&self.db)
            .await?
            .is_some()
        {
            return Err(DbErr::Custom("Employee not found".to_owned()));
        }

        // 验证公司是否存在
        let company_id = params.company_id;
        if !company::Entity::find_by_id(company_id)
            .one(&self.db)
            .await?
            .is_some()
        {
            return Err(DbErr::Custom("Company not found".to_owned()));
        }

        // 验证部门是否存在且属于该公司
        let department_id = params.department_id;
        if let Some(dept) = department::Entity::find_by_id(department_id)
            .one(&self.db)
            .await?
        {
            if dept.company_id != company_id {
                return Err(DbErr::Custom(
                    "Department does not belong to the company".to_owned(),
                ));
            }
        } else {
            return Err(DbErr::Custom("Department not found".to_owned()));
        }

        // 验证职位是否存在且属于该公司
        let position_id = params.position_id;
        if let Some(pos) = position::Entity::find_by_id(position_id)
            .one(&self.db)
            .await?
        {
            if pos.company_id != company_id {
                return Err(DbErr::Custom(
                    "Position does not belong to the company".to_owned(),
                ));
            }
        } else {
            return Err(DbErr::Custom("Position not found".to_owned()));
        }

        // 创建或更新关联
        match params.id {
            Some(id) => {
                let relation =
                    if let Some(relation) = EmployeePosition::find_by_id(id).one(&self.db).await? {
                        relation
                    } else {
                        return Err(DbErr::Custom(
                            "Employee position relation not found".to_owned(),
                        ));
                    };

                let mut relation: EmployeePositionActive = relation.into();
                relation.employee_id = Set(employee_id);
                relation.company_id = Set(company_id);
                relation.department_id = Set(department_id);
                relation.position_id = Set(position_id);
                relation.entry_at = Set(params.entry_at);
                relation.remark = Set(params.remark);

                let result = relation.update(&self.db).await?;
                Ok(result.into())
            }
            None => {
                let relation = EmployeePositionActive {
                    employee_id: Set(employee_id),
                    company_id: Set(company_id),
                    department_id: Set(department_id),
                    position_id: Set(position_id),
                    entry_at: Set(params.entry_at),
                    remark: Set(params.remark),
                    ..Default::default()
                };

                let result = relation.insert(&self.db).await?;
                Ok(result.into())
            }
        }
    }

    /// 移除员工的职位关联
    ///
    /// # 参数
    /// - `id`: 关联ID
    ///
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn remove_position(&self, id: i32) -> Result<DeleteResult, DbErr> {
        EmployeePosition::delete_by_id(id).exec(&self.db).await
    }

    /// 分页查询所有员工
    ///
    /// # 参数
    /// - `params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaEmployee>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_all(&self, params: &PageParams) -> Result<PageResult<SchemaEmployee>, DbErr> {
        let page = params.page;
        let limit = params.limit;

        let paginator = Employee::find()
            .join(
                JoinType::LeftJoin,
                employee::Relation::EmployeePosition.def(),
            )
            .select_only()
            .column(employee::Column::Id)
            .column(employee::Column::CompanyId)
            .column(employee::Column::Name)
            .column(employee::Column::Email)
            .column(employee::Column::Phone)
            .column(employee::Column::Birthdate)
            .column(employee::Column::Address)
            .column(employee::Column::Gender)
            .column(employee::Column::ExtraValue)
            .column(employee::Column::ExtraSchemaId)
            .column(employee::Column::CreatedAt)
            .column(employee::Column::UpdatedAt)
            .column(employee_position::Column::DepartmentId)
            .column(employee_position::Column::PositionId)
            .order_by_asc(employee::Column::Id)
            .into_model::<SchemaEmployee>()
            .paginate(&self.db, limit);

        let total = paginator.num_items().await?;
        let total_pages = paginator.num_pages().await?;
        let items = paginator.fetch_page(page - 1).await?;

        Ok(PageResult {
            items,
            total,
            page: page,
            limit: limit,
            total_pages,
        })
    }

    /// 按公司分页查询员工
    ///
    /// # 参数
    /// - `company_id`: 公司ID
    /// - `params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaEmployee>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_by_company(
        &self,
        company_id: i32,
        params: &PageParams,
    ) -> Result<PageResult<SchemaEmployee>, DbErr> {
        let page = params.page;
        let limit = params.limit;

        let paginator = Employee::find()
            .join(
                JoinType::LeftJoin,
                employee::Relation::EmployeePosition.def(),
            )
            .select_only()
            .column(employee::Column::Id)
            .column(employee::Column::CompanyId)
            .column(employee::Column::Name)
            .column(employee::Column::Email)
            .column(employee::Column::Phone)
            .column(employee::Column::Birthdate)
            .column(employee::Column::Address)
            .column(employee::Column::Gender)
            .column(employee::Column::ExtraValue)
            .column(employee::Column::ExtraSchemaId)
            .column(employee::Column::CreatedAt)
            .column(employee::Column::UpdatedAt)
            .column(employee_position::Column::DepartmentId)
            .column(employee_position::Column::PositionId)
            .filter(employee::Column::CompanyId.eq(company_id))
            .order_by_asc(employee::Column::Id)
            .into_model::<SchemaEmployee>()
            .paginate(&self.db, limit);

        let total = paginator.num_items().await?;
        let total_pages = paginator.num_pages().await?;
        let items = paginator.fetch_page(page - 1).await?;

        Ok(PageResult {
            items,
            total,
            page: page,
            limit: limit,
            total_pages,
        })
    }

    /// 按部门分页查询员工
    ///
    /// # 参数
    /// - `department_id`: 部门ID
    /// - `params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaEmployee>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_by_department(
        &self,
        department_id: i32,
        params: &PageParams,
    ) -> Result<PageResult<SchemaEmployee>, DbErr> {
        let page = params.page;
        let limit = params.limit;

        let paginator = Employee::find()
            .join(
                JoinType::InnerJoin,
                employee::Relation::EmployeePosition.def(),
            )
            .select_only()
            .column(employee::Column::Id)
            .column(employee::Column::CompanyId)
            .column(employee::Column::Name)
            .column(employee::Column::Email)
            .column(employee::Column::Phone)
            .column(employee::Column::Birthdate)
            .column(employee::Column::Address)
            .column(employee::Column::Gender)
            .column(employee::Column::ExtraValue)
            .column(employee::Column::ExtraSchemaId)
            .column(employee::Column::CreatedAt)
            .column(employee::Column::UpdatedAt)
            .column(employee_position::Column::DepartmentId)
            .column(employee_position::Column::PositionId)
            .filter(employee_position::Column::DepartmentId.eq(department_id))
            .order_by_asc(employee::Column::Id)
            .into_model::<SchemaEmployee>()
            .paginate(&self.db, limit);

        let total = paginator.num_items().await?;
        let total_pages = paginator.num_pages().await?;
        let items = paginator.fetch_page(page - 1).await?;

        Ok(PageResult {
            items,
            total,
            page: page,
            limit: limit,
            total_pages,
        })
    }

    /// 按名称搜索员工
    ///
    /// # 参数
    /// - `name`: 员工姓名（支持模糊搜索）
    /// - `params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaEmployee>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn search_by_name(
        &self,
        name: &str,
        params: &PageParams,
    ) -> Result<PageResult<SchemaEmployee>, DbErr> {
        let page = params.page;
        let limit = params.limit;

        let paginator = Employee::find()
            .join(
                JoinType::LeftJoin,
                employee::Relation::EmployeePosition.def(),
            )
            .select_only()
            .column(employee::Column::Id)
            .column(employee::Column::CompanyId)
            .column(employee::Column::Name)
            .column(employee::Column::Email)
            .column(employee::Column::Phone)
            .column(employee::Column::Birthdate)
            .column(employee::Column::Address)
            .column(employee::Column::Gender)
            .column(employee::Column::ExtraValue)
            .column(employee::Column::ExtraSchemaId)
            .column(employee::Column::CreatedAt)
            .column(employee::Column::UpdatedAt)
            .column(employee_position::Column::DepartmentId)
            .column(employee_position::Column::PositionId)
            .filter(employee::Column::Name.contains(name))
            .order_by_asc(employee::Column::Id)
            .into_model::<SchemaEmployee>()
            .paginate(&self.db, limit);

        let total = paginator.num_items().await?;
        let total_pages = paginator.num_pages().await?;
        let items = paginator.fetch_page(page - 1).await?;

        Ok(PageResult {
            items,
            total,
            page: page,
            limit: limit,
            total_pages,
        })
    }

    /// 获取员工的所有职位
    ///
    /// # 参数
    /// - `employee_id`: 员工ID
    ///
    /// # 返回
    /// - `Result<Vec<SchemaEmployeePosition>, DbErr>`: 成功返回职位列表，失败返回数据库错误
    pub async fn find_positions_by_employee(
        &self,
        employee_id: i32,
    ) -> Result<Vec<SchemaEmployeePosition>, DbErr> {
        let results = EmployeePosition::find()
            .filter(employee_position::Column::EmployeeId.eq(employee_id))
            .all(&self.db)
            .await?;

        Ok(results.into_iter().map(|model| model.into()).collect())
    }

    /// 获取员工的当前职位状态
    ///
    /// # 参数
    /// - `employee_id`: 员工ID
    ///
    /// # 返回
    /// - `Result<Option<SchemaEmployeePosition>, DbErr>`: 成功返回最新的职位状态，失败返回数据库错误
    pub async fn find_current_position(
        &self,
        employee_id: i32,
    ) -> Result<Option<SchemaEmployeePosition>, DbErr> {
        let result = EmployeePosition::find()
            .filter(employee_position::Column::EmployeeId.eq(employee_id))
            .order_by_desc(employee_position::Column::CreatedAt)
            .one(&self.db)
            .await?;

        Ok(result.map(|model| model.into()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use lib_schema::models::employee::Gender;

    async fn setup_test_service() -> EmployeeService {
        let db = sea_orm::Database::connect("sqlite::memory:").await.unwrap();
        EmployeeService::new(db)
    }

    #[tokio::test]
    async fn test_create_employee() {
        let service = setup_test_service().await;
        let params = InsertEmployee {
            id: None,
            company_id: 1,
            name: "Test Employee".to_string(),
            email: Some("test@example.com".to_string()),
            phone: Some("1234567890".to_string()),
            birthdate: Some(Utc::now().naive_utc()),
            address: Some("Test Address".to_string()),
            gender: Gender::Male,
            department_id: Some(1),
            position_id: Some(1),
            entry_date: Some(Utc::now().naive_utc()),
            candidate_id: None,
            extra_value: None,
            extra_schema_id: None,
            marital_status: None,
            emergency_contact: None,
        };

        let result = service.insert(params).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_update_employee() {
        let service = setup_test_service().await;
        let params = InsertEmployee {
            id: Some(1),
            company_id: 1,
            name: "Updated Employee".to_string(),
            email: Some("updated@example.com".to_string()),
            phone: Some("0987654321".to_string()),
            birthdate: Some(Utc::now().naive_utc()),
            address: Some("Updated Address".to_string()),
            gender: Gender::Female,
            department_id: Some(2),
            position_id: Some(2),
            entry_date: Some(Utc::now().naive_utc()),
            candidate_id: None,
            extra_value: None,
            extra_schema_id: None,
            marital_status: None,
            emergency_contact: None,
        };

        let result = service.insert(params).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_delete_employee() {
        let service = setup_test_service().await;
        let result = service.delete(1).await;
        assert!(result.is_ok());
    }
}
