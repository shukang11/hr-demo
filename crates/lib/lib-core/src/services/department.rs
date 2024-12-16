use lib_entity::entities::department::{self, ActiveModel, Entity as Department, Model};
use lib_schema::models::department::InsertDepartment;
use lib_schema::{PageParams, PageResult};
use sea_orm::*;

/// 部门服务
///
/// 提供部门相关的核心业务功能，包括：
/// - 创建/更新部门
/// - 删除部门
/// - 查询部门（单个查询、分页查询、按名称搜索）
#[derive(Debug)]
pub struct DepartmentService {
    db: DatabaseConnection,
}

impl DepartmentService {
    /// 创建服务实例
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 创建或更新部门
    ///
    /// # 参数
    /// - `params`: 部门参数，如果包含id则为更新，否则为创建
    ///
    /// # 返回
    /// - `Result<Model, DbErr>`: 成功返回部门模型，失败返回数据库错误
    pub async fn insert(&self, params: InsertDepartment) -> Result<Model, DbErr> {
        match params.id {
            // 更新现有部门
            Some(id) => {
                let department = if let Some(department) = self.find_by_id(id).await? {
                    department
                } else {
                    return Err(DbErr::Custom("Department not found".to_owned()));
                };

                let mut department: ActiveModel = department.into();

                // 更新字段
                department.name = Set(params.name);
                department.parent_id = Set(params.parent_id);
                department.company_id = Set(params.company_id);
                department.leader_id = Set(params.leader_id);
                department.remark = Set(params.remark);

                department.update(&self.db).await
            }
            // 创建新部门
            None => {
                let department = ActiveModel {
                    name: Set(params.name),
                    parent_id: Set(params.parent_id),
                    company_id: Set(params.company_id),
                    leader_id: Set(params.leader_id),
                    remark: Set(params.remark),
                    ..Default::default()
                };

                department.insert(&self.db).await
            }
        }
    }

    /// 删除部门
    ///
    /// # 参数
    /// - `id`: 部门ID
    ///
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        Department::delete_by_id(id).exec(&self.db).await
    }

    /// 根据ID查询部门
    ///
    /// # 参数
    /// - `id`: 部门ID
    ///
    /// # 返回
    /// - `Result<Option<Model>, DbErr>`: 成功返回部门模型（如果存在），失败返回数据库错误
    pub async fn find_by_id(&self, id: i32) -> Result<Option<Model>, DbErr> {
        Department::find_by_id(id).one(&self.db).await
    }

    /// 根据公司ID分页查询部门
    ///
    /// # 参数
    /// - `company_id`: 公司ID
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<Model>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_by_company(
        &self,
        company_id: i32,
        page_params: &PageParams,
    ) -> Result<PageResult<Model>, DbErr> {
        let paginator = Department::find()
            .filter(department::Column::CompanyId.eq(company_id))
            .order_by_asc(department::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;

        Ok(PageResult::new(items, total, page_params))
    }

    /// 根据名称搜索部门
    ///
    /// # 参数
    /// - `company_id`: 公司ID
    /// - `name`: 部门名称关键字
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<Model>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn search_by_name(
        &self,
        company_id: i32,
        name: &str,
        page_params: &PageParams,
    ) -> Result<PageResult<Model>, DbErr> {
        let paginator = Department::find()
            .filter(department::Column::CompanyId.eq(company_id))
            .filter(department::Column::Name.contains(name))
            .order_by_asc(department::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;

        Ok(PageResult::new(items, total, page_params))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_runner;

    /// 创建测试服务实例
    async fn setup_test_service() -> DepartmentService {
        let db = test_runner::setup_database().await;
        DepartmentService::new(db)
    }

    /// 测试创建部门功能
    #[tokio::test]
    async fn test_create_department() {
        let service = setup_test_service().await;
        let params = InsertDepartment {
            id: None,
            name: "测试部门".to_string(),
            parent_id: None,
            company_id: 1,
            leader_id: None,
            remark: None,
        };

        let result = service.insert(params.clone()).await;
        assert!(result.is_ok(), "创建部门失败: {:?}", result.err());

        let department = result.unwrap();
        assert_eq!(department.name, params.name);
        assert!(department.id > 0);
    }

    /// 测试更新部门功能
    #[tokio::test]
    async fn test_update_department() {
        let service = setup_test_service().await;

        // 创建测试数据
        let create_params = InsertDepartment {
            id: None,
            name: "原部门名".to_string(),
            parent_id: None,
            company_id: 1,
            leader_id: None,
            remark: None,
        };
        let department = service
            .insert(create_params)
            .await
            .expect("创建测试部门失败");

        // 测试成功更新
        let update_params = InsertDepartment {
            id: Some(department.id),
            name: "新部门名".to_string(),
            parent_id: None,
            company_id: department.company_id,
            leader_id: None,
            remark: None,
        };
        let result = service.insert(update_params).await;
        assert!(result.is_ok(), "更新部门失败: {:?}", result.err());

        let updated_department = result.unwrap();
        assert_eq!(updated_department.name, "新部门名");

        // 测试更新不存在的部门
        let invalid_update = InsertDepartment {
            id: Some(99999),
            name: "测试名称".to_string(),
            parent_id: None,
            company_id: 1,
            leader_id: None,
            remark: None,
        };
        let result = service.insert(invalid_update).await;
        assert!(result.is_err(), "更新不存在的部门应该失败");
    }

    /// 测试删除部门功能
    #[tokio::test]
    async fn test_delete_department() {
        let service = setup_test_service().await;

        // 创建测试数据
        let params = InsertDepartment {
            id: None,
            name: "待删除部门".to_string(),
            parent_id: None,
            company_id: 1,
            leader_id: None,
            remark: None,
        };
        let department = service.insert(params).await.expect("创建测试部门失败");

        // 测试删除
        let result = service.delete(department.id).await;
        assert!(result.is_ok(), "删除部门失败: {:?}", result.err());

        // 验证删除后无法找到
        let find_result = service
            .find_by_id(department.id)
            .await
            .expect("查询删除的部门失败");
        assert!(find_result.is_none(), "删除后仍能找到部门");
    }

    /// 测试查询部门功能
    #[tokio::test]
    async fn test_query_departments() {
        let service = setup_test_service().await;
        let company_id = 1;

        // 创建测试数据
        let departments = vec!["研发部", "市场部", "人事部", "财务部", "行政部"];

        for name in departments {
            let params = InsertDepartment {
                id: None,
                name: name.to_string(),
                parent_id: None,
                company_id,
                leader_id: None,
                remark: None,
            };
            service
                .insert(params)
                .await
                .expect(&format!("创建部门 {} 失败", name));
        }

        // 测试分页查询
        let page_params = PageParams::new(1, 3);
        let result = service
            .find_by_company(company_id, &page_params)
            .await
            .expect("分页查询失败");
        assert_eq!(result.total, 5, "总记录数不正确");
        assert_eq!(result.items.len(), 3, "分页大小不正确");
        assert_eq!(result.total_pages, 2, "总页数不正确");

        // 测试名称搜索
        let page_params = PageParams::new(1, 10);
        let result = service
            .search_by_name(company_id, "研发", &page_params)
            .await
            .expect("搜索部门失败");
        assert_eq!(result.total, 1, "搜索结果数量不正确");
        assert!(
            result.items.iter().any(|d| d.name.contains("研发")),
            "搜索结果中没有包含关键字的部门"
        );
    }
}
