use lib_entity::entities::{
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
    use crate::test_runner;
    use chrono::Utc;
    use lib_schema::Gender;

    /// 创建测试服务实例
    async fn setup_test_service() -> EmployeeService {
        let db = test_runner::setup_database().await;
        EmployeeService::new(db)
    }

    /// 测试创建员工功能
    #[tokio::test]
    async fn test_create_employee() {
        let service = setup_test_service().await;
        let params = InsertEmployee {
            id: None,
            company_id: 1,
            name: "张三".to_string(),
            email: Some("zhangsan@example.com".to_string()),
            phone: Some("13800138000".to_string()),
            birthdate: Some(Utc::now().naive_utc()),
            address: Some("北京市".to_string()),
            gender: Gender::Male,
            department_id: None,
            position_id: None,
            entry_date: None,
            extra_value: None,
            extra_schema_id: None,
        };

        let result = service.insert(params.clone()).await;
        assert!(result.is_ok(), "创建员工失败: {:?}", result.err());

        let employee = result.unwrap();
        assert_eq!(employee.name, params.name);
        assert_eq!(employee.email, params.email);
        assert_eq!(employee.phone, params.phone);
        assert!(employee.id > 0);
    }

    /// 测试更新员工功能
    #[tokio::test]
    async fn test_update_employee() {
        let service = setup_test_service().await;

        // 先创建公司，再创建部门和职位
        let company_service = crate::services::company::CompanyService::new(service.db.clone());
        let company_entity = company_service
            .insert(lib_schema::models::company::InsertCompany {
                id: None,
                name: "测试公司".to_string(),
                extra_value: None,
                extra_schema_id: None,
            })
            .await
            .expect("创建测试公司失败");

        let department_service =
            crate::services::department::DepartmentService::new(service.db.clone());
        let department = department_service
            .insert(lib_schema::models::department::InsertDepartment {
                id: None,
                name: "测试部门".to_string(),
                parent_id: None,
                company_id: company_entity.id,
                leader_id: None,
                remark: None,
            })
            .await
            .expect("创建测试部门失败");

        let position_service = crate::services::position::PositionService::new(service.db.clone());
        let position = position_service
            .insert(lib_schema::models::position::InsertPosition {
                id: None,
                name: "测试职位".to_string(),
                company_id: company_entity.id,
                remark: None,
            })
            .await
            .expect("创建测试职位失败");

        // 创建测试数据
        let create_params = InsertEmployee {
            id: None,
            company_id: company_entity.id,
            name: "李四".to_string(),
            email: Some("lisi@example.com".to_string()),
            phone: Some("13900139000".to_string()),
            birthdate: Some(Utc::now().naive_utc()),
            address: Some("上海市".to_string()),
            gender: Gender::Male,
            department_id: Some(department.id),
            position_id: Some(position.id),
            entry_date: None,
            extra_value: None,
            extra_schema_id: None,
        };
        let employee = service
            .insert(create_params)
            .await
            .expect("创建测试员工失败");
        assert_eq!(employee.company_id, company_entity.id);
        assert_eq!(employee.department_id, Some(department.id));
        assert_eq!(employee.position_id, Some(position.id));

        println!("Employee: {:?}", employee);

        // 测试成功更新
        let update_params = InsertEmployee {
            id: Some(employee.id),
            company_id: company_entity.id,
            name: "李四改".to_string(),
            email: Some("lisi.new@example.com".to_string()),
            phone: Some("13900139001".to_string()),
            birthdate: Some(Utc::now().naive_utc()),
            address: Some("广州市".to_string()),
            gender: Gender::Male,
            department_id: Some(department.id),
            position_id: Some(position.id),
            entry_date: None,
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.insert(update_params).await;
        assert!(result.is_ok(), "更新员工失败: {:?}", result.err());

        let updated_employee = result.unwrap();
        assert_eq!(updated_employee.name, "李四改");
        assert_eq!(
            updated_employee.email,
            Some("lisi.new@example.com".to_string())
        );
        assert_eq!(updated_employee.address, Some("广州市".to_string()));

        // 测试更新不存在的员工
        let invalid_update = InsertEmployee {
            id: Some(99999),
            company_id: company_entity.id,
            name: "不存在".to_string(),
            email: None,
            phone: None,
            birthdate: None,
            address: None,
            gender: Gender::Unknown,
            department_id: None,
            position_id: None,
            entry_date: None,
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.insert(invalid_update).await;
        assert!(result.is_err(), "更新不存在的员工应该失败");
    }

    /// 测试删除员工功能
    #[tokio::test]
    async fn test_delete_employee() {
        let service = setup_test_service().await;

        // 创建测试数据
        let params = InsertEmployee {
            id: None,
            company_id: 1,
            name: "王五".to_string(),
            email: None,
            phone: None,
            birthdate: None,
            address: None,
            gender: Gender::Unknown,
            department_id: None,
            position_id: None,
            entry_date: None,
            extra_value: None,
            extra_schema_id: None,
        };
        let employee = service.insert(params).await.expect("创建测试员工失败");
        // 测试删除
        let result = service.delete(employee.id).await;
        assert!(result.is_ok(), "删除员工失败: {:?}", result.err());

        // 验证删除后无法找到
        let find_result = service
            .find_by_id(employee.id)
            .await
            .expect("查询删除的员工失败");
        assert!(find_result.is_none(), "删除后仍能找到员工");
    }
}
