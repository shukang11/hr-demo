use sea_orm::*;
use lib_entity::entities::company::{self, ActiveModel, Entity as Company, Model};
use lib_schema::{PageParams, PageResult};
use lib_schema::models::company::{CreateCompany, UpdateCompany};

/// 公司服务
/// 
/// 提供公司相关的核心业务功能，包括：
/// - 创建公司
/// - 更新公司信息
/// - 删除公司
/// - 查询公司（单个查询、分页查询、按名称搜索）
#[derive(Debug)]
pub struct CompanyService {
    db: DatabaseConnection,
}

impl CompanyService {
    /// 创建服务实例
    /// 
    /// # 参数
    /// - `db`: 数据库连接
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 创建新公司
    /// 
    /// # 参数
    /// - `params`: 创建公司的参数
    /// 
    /// # 返回
    /// - `Result<Model, DbErr>`: 成功返回公司模型，失败返回数据库错误
    /// 
    /// # 示例
    /// ```no_run
    /// use lib_schema::models::company::CreateCompany;
    /// use lib_core::CompanyService;
    /// 
    /// # async fn run() -> Result<(), Box<dyn std::error::Error>> {
    /// # let db = sea_orm::Database::connect("sqlite::memory:").await?;
    /// let service = CompanyService::new(db);
    /// let params = CreateCompany {
    ///     name: "新公司".to_string(),
    ///     extra_value: None,
    ///     extra_schema_id: None,
    /// };
    /// let company = service.create(params).await?;
    /// println!("创建的公司ID: {}", company.id);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn create(&self, params: CreateCompany) -> Result<Model, DbErr> {
        let company = ActiveModel {
            name: Set(params.name),
            extra_value: Set(params.extra_value),
            extra_schema_id: Set(params.extra_schema_id.map(|id| id.as_u128() as i32)),
            ..Default::default()
        };
        
        Company::insert(company)
            .exec_with_returning(&self.db)
            .await
    }

    /// 更新公司信息
    /// 
    /// # 参数
    /// - `id`: 公司ID
    /// - `params`: 更新参数
    /// 
    /// # 返回
    /// - `Result<Model, DbErr>`: 成功返回更新后的公司模型，失败返回数据库错误
    /// 
    /// # 错误
    /// - 如果公司不存在，返回 `DbErr::Custom` 错误
    pub async fn update(&self, id: i32, params: UpdateCompany) -> Result<Model, DbErr> {
        // 先查找公司���否存在
        let company = if let Some(company) = self.find_by_id(id).await? {
            company
        } else {
            return Err(DbErr::Custom("Company not found".to_owned()));
        };

        let mut company: ActiveModel = company.into();
        
        // 根据参数更新字段
        if let Some(name) = params.name {
            company.name = Set(name);
        }
        if let Some(extra_value) = params.extra_value {
            company.extra_value = Set(Some(extra_value));
        }
        if let Some(extra_schema_id) = params.extra_schema_id {
            company.extra_schema_id = Set(Some(extra_schema_id.as_u128() as i32));
        }

        company.update(&self.db).await
    }

    /// 删除公司
    /// 
    /// # 参数
    /// - `id`: 要删除的公司ID
    /// 
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        Company::delete_by_id(id).exec(&self.db).await
    }

    /// 根据ID查找公司
    /// 
    /// # 参数
    /// - `id`: 公司ID
    /// 
    /// # 返回
    /// - `Result<Option<Model>, DbErr>`: 成功返回可能存在的公司模型，失败返回数据库错误
    pub async fn find_by_id(&self, id: i32) -> Result<Option<Model>, DbErr> {
        Company::find_by_id(id).one(&self.db).await
    }

    /// 分页查询所有公司
    /// 
    /// # 参数
    /// - `page_params`: 分页参数
    /// 
    /// # 返回
    /// - `Result<PageResult<Model>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    /// 
    /// # 示例
    /// ```no_run
    /// use lib_schema::PageParams;
    /// use lib_core::CompanyService;
    /// 
    /// # async fn run() -> Result<(), Box<dyn std::error::Error>> {
    /// # let db = sea_orm::Database::connect("sqlite::memory:").await?;
    /// let service = CompanyService::new(db);
    /// let params = PageParams::new(1, 10);
    /// let result = service.find_all(&params).await?;
    /// println!("总记录数: {}, 当前页记录数: {}", result.total, result.items.len());
    /// # Ok(())
    /// # }
    /// ```
    pub async fn find_all(&self, page_params: &PageParams) -> Result<PageResult<Model>, DbErr> {
        let paginator = Company::find()
            .order_by_asc(company::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;

        Ok(PageResult::new(items, total, page_params))
    }

    /// 按名称搜索公司
    /// 
    /// # 参数
    /// - `name`: 搜索关键字
    /// - `page_params`: 分页参数
    /// 
    /// # 返回
    /// - `Result<PageResult<Model>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    /// 
    /// # 示例
    /// ```no_run
    /// use lib_schema::PageParams;
    /// use lib_core::CompanyService;
    /// 
    /// # async fn run() -> Result<(), Box<dyn std::error::Error>> {
    /// # let db = sea_orm::Database::connect("sqlite::memory:").await?;
    /// let service = CompanyService::new(db);
    /// let params = PageParams::new(1, 10);
    /// let result = service.search_by_name("科技", &params).await?;
    /// println!("找到 {} 家包含'科技'的公司", result.total);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn search_by_name(
        &self,
        name: &str,
        page_params: &PageParams,
    ) -> Result<PageResult<Model>, DbErr> {
        let paginator = Company::find()
            .filter(company::Column::Name.contains(name))
            .order_by_asc(company::Column::Id)
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
    async fn setup_test_service() -> CompanyService {
        let db = test_runner::setup_database().await;
        CompanyService::new(db)
    }

    /// 测试创建公司功能
    #[tokio::test]
    async fn test_create_company() {
        let service = setup_test_service().await;
        let params = CreateCompany {
            name: "测试公司".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        
        let result = service.create(params.clone()).await;
        assert!(result.is_ok(), "创建公司失败: {:?}", result.err());
        
        let company = result.unwrap();
        assert_eq!(company.name, params.name);
        assert!(company.id > 0);
    }

    /// 测试更新公司功能
    #[tokio::test]
    async fn test_update_company() {
        let service = setup_test_service().await;
        
        // 创建测试数据
        let create_params = CreateCompany {
            name: "原公司名".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let company = service.create(create_params).await
            .expect("创建测试公司失败");
        
        // 测试成功更新
        let update_params = UpdateCompany {
            name: Some("新公司名".to_string()),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.update(company.id, update_params).await;
        assert!(result.is_ok(), "更新公司失败: {:?}", result.err());
        
        let updated_company = result.unwrap();
        assert_eq!(updated_company.name, "新公司名");
        
        // 测试更新不存在的公司
        let invalid_update = UpdateCompany {
            name: Some("测试名称".to_string()),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.update(9999, invalid_update).await;
        assert!(result.is_err(), "更新不存在的公司应该失败");
    }

    /// 测试删除公司功能
    #[tokio::test]
    async fn test_delete_company() {
        let service = setup_test_service().await;
        
        // 创建测试数据
        let params = CreateCompany {
            name: "待删除公司".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let company = service.create(params).await
            .expect("创建测试公司失败");
        
        // 测试删除
        let result = service.delete(company.id).await;
        assert!(result.is_ok(), "删除公司失败: {:?}", result.err());
        
        // 验证删除后无法找到
        let find_result = service.find_by_id(company.id).await
            .expect("查询删除的公司失败");
        assert!(find_result.is_none(), "删除后仍能找到公司");
    }

    /// 测试查询公司功能
    #[tokio::test]
    async fn test_query_companies() {
        let service = setup_test_service().await;
        
        // 创建测试数据
        let companies = vec![
            "阿里巴巴",
            "腾讯科技",
            "百度在线",
            "字节跳动",
            "美团点评"
        ];
        
        for name in companies {
            let params = CreateCompany {
                name: name.to_string(),
                extra_value: None,
                extra_schema_id: None,
            };
            service.create(params).await
                .expect(&format!("创建公司 {} 失败", name));
        }
        
        // 测试分页查询
        let page_params = PageParams::new(1, 3);
        let result = service.find_all(&page_params).await
            .expect("分页查询失败");
        assert_eq!(result.total, 5, "总记录数不正确");
        assert_eq!(result.items.len(), 3, "分页大小不正确");
        assert_eq!(result.total_pages, 2, "总页数不正确");
        
        // 测试名称搜索
        let page_params = PageParams::new(1, 10);
        let result = service.search_by_name("科技", &page_params).await
            .expect("搜���公司失败");
        assert_eq!(result.total, 1, "搜索结果数量不正确");
        assert!(result.items.iter().any(|c| c.name.contains("科技")), 
            "搜索结果中没有包含关键字的公司");
    }

    /// 测试边界情况
    #[tokio::test]
    async fn test_edge_cases() {
        let service = setup_test_service().await;
        
        // 测试空名称
        let params = CreateCompany {
            name: "".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.create(params).await;
        assert!(result.is_ok(), "创建空名称公司失败: {:?}", result.err());
        
        // 测试超长名称（255字符）
        let params = CreateCompany {
            name: "a".repeat(255),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.create(params).await;
        assert!(result.is_ok(), "创建长名称公司失败: {:?}", result.err());
        
        // 测试特殊字符
        let params = CreateCompany {
            name: "测试公司 #$%^&*()".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.create(params).await;
        assert!(result.is_ok(), "创建特殊字符名称公司失败: {:?}", result.err());
    }
} 