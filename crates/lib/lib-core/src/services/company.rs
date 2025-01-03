use lib_entity::entities::company::{self, ActiveModel, Entity as CompanyEntity};
use lib_schema::models::company::{Company as SchemaCompany, InsertCompany};
use lib_schema::{PageParams, PageResult};
use sea_orm::*;

/// 公司服务
///
/// 提供公司相关的核心业务功能，包括：
/// - 创建/更新公司
/// - 删除公司
/// - 查询公司（单个查询、分页查询、按名称搜索）
#[derive(Debug)]
pub struct CompanyService {
    db: DatabaseConnection,
}

impl CompanyService {
    /// 创建服务实例
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 检查公司名称是否重复
    async fn check_duplicate(
        &self,
        id: Option<i32>,
        name: &str,
    ) -> Result<bool, DbErr> {
        use sea_orm::QueryFilter;

        tracing::info!(
            "检查重复公司: id={:?}, name={}",
            id, name
        );

        let mut query = CompanyEntity::find()
            .filter(company::Column::Name.eq(name));

        // 如果是更新操作，排除当前记录
        if let Some(current_id) = id {
            query = query.filter(company::Column::Id.ne(current_id));
        }

        let count = query.count(&self.db).await?;
        tracing::info!("查询结果: 找到 {} 个重名公司", count);
        Ok(count > 0)
    }

    /// 创建或更新公司
    ///
    /// # 参数
    /// - `params`: 公司参数，如果包含id则为更新，否则为创建
    ///
    /// # 返回
    /// - `Result<SchemaCompany, DbErr>`: 成功返回公司模型，失败返回数据库错误
    pub async fn insert(&self, params: InsertCompany) -> Result<SchemaCompany, DbErr> {
        // 检查是否存在重名公司
        if self.check_duplicate(params.id, &params.name).await? {
            return Err(DbErr::Custom("已存在相同名称的公司".to_string()));
        }

        match params.id {
            Some(id) => {
                let company = if let Ok(Some(m)) = CompanyEntity::find_by_id(id).one(&self.db).await
                {
                    m
                } else {
                    return Err(DbErr::Custom("Company not found".to_owned()));
                };

                let mut company: ActiveModel = company.into();
                company.name = Set(params.name);
                company.extra_value = Set(params.extra_value);
                company.extra_schema_id = Set(params.extra_schema_id);

                let result = company.update(&self.db).await?;
                Ok(result.into())
            }
            None => {
                let company = ActiveModel {
                    name: Set(params.name),
                    extra_value: Set(params.extra_value),
                    extra_schema_id: Set(params.extra_schema_id),
                    ..Default::default()
                };

                let result = company.insert(&self.db).await?;
                Ok(result.into())
            }
        }
    }

    /// 删除公司
    ///
    /// # 参数
    /// - `id`: 公司ID
    ///
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        CompanyEntity::delete_by_id(id).exec(&self.db).await
    }

    /// 根据ID查询公司
    ///
    /// # 参数
    /// - `id`: 公司ID
    ///
    /// # 返回
    /// - `Result<Option<SchemaCompany>, DbErr>`: 成功返回公司模型（如果存在），失败返回数据库错误
    pub async fn find_by_id(&self, id: i32) -> Result<Option<SchemaCompany>, DbErr> {
        let result = CompanyEntity::find_by_id(id).one(&self.db).await?;
        Ok(result.map(|model| model.into()))
    }

    /// 分页查询所有公司
    ///
    /// # 参数
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaCompany>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_all(
        &self,
        page_params: &PageParams,
    ) -> Result<PageResult<SchemaCompany>, DbErr> {
        let paginator = CompanyEntity::find()
            .order_by_asc(company::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;
        let items = items.into_iter().map(|model| model.into()).collect();

        Ok(PageResult::new(items, total, page_params))
    }

    /// 根据名称搜索公司
    ///
    /// # 参数
    /// - `name`: 公司名称关键字
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaCompany>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn search_by_name(
        &self,
        name: &str,
        page_params: &PageParams,
    ) -> Result<PageResult<SchemaCompany>, DbErr> {
        let paginator = CompanyEntity::find()
            .filter(company::Column::Name.contains(name))
            .order_by_asc(company::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;
        let items = items.into_iter().map(|model| model.into()).collect();

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
        let params = InsertCompany {
            id: None,
            name: "测试公司".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };

        let result = service.insert(params.clone()).await;
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
        let create_params = InsertCompany {
            id: None,
            name: "原公司名".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let company = service
            .insert(create_params)
            .await
            .expect("创建测试公司失败");

        // 测试成功更新
        let update_params = InsertCompany {
            id: Some(company.id),
            name: "新公司名".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.insert(update_params).await;
        assert!(result.is_ok(), "更新公司失败: {:?}", result.err());

        let updated_company = result.unwrap();
        assert_eq!(updated_company.name, "新公司名");

        // 测试更新不存在的公司
        let invalid_update = InsertCompany {
            id: Some(99999),
            name: "测试名称".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let result = service.insert(invalid_update).await;
        assert!(result.is_err(), "更新不存在的公司应该失败");
    }

    /// 测试删除公司功能
    #[tokio::test]
    async fn test_delete_company() {
        let service = setup_test_service().await;

        // 创建测试数据
        let params = InsertCompany {
            id: None,
            name: "待删除公司".to_string(),
            extra_value: None,
            extra_schema_id: None,
        };
        let company = service.insert(params).await.expect("创建测试公司失败");

        // 测试删除
        let result = service.delete(company.id).await;
        assert!(result.is_ok(), "删除公司失败: {:?}", result.err());

        // 验证删除后无法找到
        let find_result = service
            .find_by_id(company.id)
            .await
            .expect("查询删除的公司失败");
        assert!(find_result.is_none(), "删除后仍能找到公司");
    }

    /// 测试查询公司功能
    #[tokio::test]
    async fn test_query_companies() {
        let service = setup_test_service().await;

        // 创建测试数据
        let companies = vec!["阿里巴巴", "腾讯科技", "百度在线", "字节跳动", "美团点评"];

        for name in companies {
            let params = InsertCompany {
                id: None,
                name: name.to_string(),
                extra_value: None,
                extra_schema_id: None,
            };
            service
                .insert(params)
                .await
                .expect(&format!("创建公司 {} 失败", name));
        }

        // 测试分页查询
        let page_params = PageParams::new(1, 3);
        let result = service.find_all(&page_params).await.expect("分页查询失败");
        assert_eq!(result.total, 5, "总记录数不正确");
        assert_eq!(result.items.len(), 3, "分页大小不正确");
        assert_eq!(result.total_pages, 2, "总页数不正确");

        // 测试名称搜索
        let page_params = PageParams::new(1, 10);
        let result = service
            .search_by_name("科技", &page_params)
            .await
            .expect("搜索公司失败");
        assert_eq!(result.total, 1, "搜索结果数量不正确");
        assert!(
            result.items.iter().any(|c| c.name.contains("科技")),
            "搜索结果中没有包含关键字的公司"
        );
    }
}
