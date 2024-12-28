use lib_entity::entities::position::{self, ActiveModel, Entity as Position};
use lib_schema::models::position::{InsertPosition, Position as SchemaPosition};
use lib_schema::{PageParams, PageResult};
use sea_orm::*;

/// 职位服务
///
/// 提供职位相关的核心业务功能，包括：
/// - 创建/更新职位
/// - 删除职位
/// - 查询职位（单个查询、分页查询、按名称搜索）
#[derive(Debug)]
pub struct PositionService {
    db: DatabaseConnection,
}

impl PositionService {
    /// 创建服务实例
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// 创建或更新职位
    ///
    /// # 参数
    /// - `params`: 职位参数，如果包含id则为更新，否则为创建
    ///
    /// # 返回
    /// - `Result<SchemaPosition, DbErr>`: 成功返回职位模型，失败返回数据库错误
    pub async fn insert(&self, params: InsertPosition) -> Result<SchemaPosition, DbErr> {
        match params.id {
            // 更新现有职位
            Some(id) => {
                let position = if let Ok(Some(m)) = Position::find_by_id(id).one(&self.db).await {
                    m
                } else {
                    return Err(DbErr::Custom("Position not found".to_owned()));
                };

                let mut position: ActiveModel = position.into();
                position.name = Set(params.name);
                position.company_id = Set(params.company_id);
                position.remark = Set(params.remark);

                let result = position.update(&self.db).await?;
                Ok(result.into())
            }
            // 创建新职位
            None => {
                let position = ActiveModel {
                    name: Set(params.name),
                    company_id: Set(params.company_id),
                    remark: Set(params.remark),
                    ..Default::default()
                };

                let result = position.insert(&self.db).await?;
                Ok(result.into())
            }
        }
    }

    /// 删除职位
    ///
    /// # 参数
    /// - `id`: 职位ID
    ///
    /// # 返回
    /// - `Result<DeleteResult, DbErr>`: 成功返回删除结果，失败返回数据库错误
    pub async fn delete(&self, id: i32) -> Result<DeleteResult, DbErr> {
        Position::delete_by_id(id).exec(&self.db).await
    }

    /// 根据ID查询职位
    ///
    /// # 参数
    /// - `id`: 职位ID
    ///
    /// # 返回
    /// - `Result<Option<SchemaPosition>, DbErr>`: 成功返回职位模型（如果存在），失败返回数据库错误
    pub async fn find_by_id(&self, id: i32) -> Result<Option<SchemaPosition>, DbErr> {
        let result = Position::find_by_id(id).one(&self.db).await?;
        Ok(result.map(|model| model.into()))
    }

    /// 根据公司ID分页查询职位
    ///
    /// # 参数
    /// - `company_id`: 公司ID
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaPosition>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn find_by_company(
        &self,
        company_id: i32,
        page_params: &PageParams,
    ) -> Result<PageResult<SchemaPosition>, DbErr> {
        let paginator = Position::find()
            .filter(position::Column::CompanyId.eq(company_id))
            .order_by_asc(position::Column::Id)
            .paginate(&self.db, page_params.get_limit());

        let total = paginator.num_items().await?;
        let items = paginator.fetch_page(page_params.page - 1).await?;
        let items = items.into_iter().map(|model| model.into()).collect();

        Ok(PageResult::new(items, total, page_params))
    }

    /// 根据名称搜索职位
    ///
    /// # 参数
    /// - `company_id`: 公司ID
    /// - `name`: 职位名称关键字
    /// - `page_params`: 分页参数
    ///
    /// # 返回
    /// - `Result<PageResult<SchemaPosition>, DbErr>`: 成功返回分页结果，失败返回数据库错误
    pub async fn search_by_name(
        &self,
        company_id: i32,
        name: &str,
        page_params: &PageParams,
    ) -> Result<PageResult<SchemaPosition>, DbErr> {
        let paginator = Position::find()
            .filter(position::Column::CompanyId.eq(company_id))
            .filter(position::Column::Name.contains(name))
            .order_by_asc(position::Column::Id)
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
    async fn setup_test_service() -> PositionService {
        let db = test_runner::setup_database().await;
        PositionService::new(db)
    }

    /// 测试创建职位功能
    #[tokio::test]
    async fn test_create_position() {
        let service = setup_test_service().await;
        let params = InsertPosition {
            id: None,
            name: "测试职位".to_string(),
            company_id: 1,
            remark: None,
        };

        let result = service.insert(params.clone()).await;
        assert!(result.is_ok(), "创建职位失败: {:?}", result.err());

        let position = result.unwrap();
        assert_eq!(position.name, params.name);
        assert!(position.id > 0);
    }

    /// 测试更新职位功能
    #[tokio::test]
    async fn test_update_position() {
        let service = setup_test_service().await;

        // 创建测试数据
        let create_params = InsertPosition {
            id: None,
            name: "原职位名".to_string(),
            company_id: 1,
            remark: None,
        };
        let position = service
            .insert(create_params)
            .await
            .expect("创建测试职位失败");

        // 测试成功更新
        let update_params = InsertPosition {
            id: Some(position.id),
            name: "新职位名".to_string(),
            company_id: position.company_id,
            remark: None,
        };
        let result = service.insert(update_params).await;
        assert!(result.is_ok(), "更新职位失败: {:?}", result.err());

        let updated_position = result.unwrap();
        assert_eq!(updated_position.name, "新职位名");

        // 测试更新不存在的职位
        let invalid_update = InsertPosition {
            id: Some(99999),
            name: "测试名称".to_string(),
            company_id: 1,
            remark: None,
        };
        let result = service.insert(invalid_update).await;
        assert!(result.is_err(), "更新不存在的职位应该失败");
    }

    /// 测试删除职位功能
    #[tokio::test]
    async fn test_delete_position() {
        let service = setup_test_service().await;

        // 创建测试数据
        let params = InsertPosition {
            id: None,
            name: "待删除职位".to_string(),
            company_id: 1,
            remark: None,
        };
        let position = service.insert(params).await.expect("创建测试职位失败");

        // 测试删除
        let result = service.delete(position.id).await;
        assert!(result.is_ok(), "删除职位失败: {:?}", result.err());

        // 验证删除后无法找到
        let find_result = service
            .find_by_id(position.id)
            .await
            .expect("查询删除的职位失败");
        assert!(find_result.is_none(), "删除后仍能找到职位");
    }

    /// 测试查询职位功能
    #[tokio::test]
    async fn test_query_positions() {
        let service = setup_test_service().await;
        let company_id = 1;

        // 创建测试数据
        let positions = vec![
            "软件工程师",
            "产品经理",
            "UI设计师",
            "测试工程师",
            "运维工程师",
        ];

        for name in positions {
            let params = InsertPosition {
                id: None,
                name: name.to_string(),
                company_id,
                remark: None,
            };
            service
                .insert(params)
                .await
                .expect(&format!("创建职位 {} 失败", name));
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
            .search_by_name(company_id, "工程师", &page_params)
            .await
            .expect("搜索职位失败");
        assert_eq!(result.total, 3, "搜索结果数量不正确");
        assert!(
            result.items.iter().all(|p| p.name.contains("工程师")),
            "搜索结果中有不包含关键字的职位"
        );
    }
}
