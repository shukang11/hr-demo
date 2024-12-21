use axum::{
    extract::{Path, Query},
    routing::{get, post, delete},
    Extension, Json, Router,
};
use lib_core::CompanyService;
use lib_schema::{models::company::InsertCompany, Company, PageParams, PageResult};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 创建或更新公司
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertCompany>,
) -> APIResponse<Company> {
    let company_service = CompanyService::new(app.pool.clone());
    match company_service.insert(params).await {
        Ok(result) => {
            let model = Company::from(result);
            APIResponse::new().with_data(model)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取公司列表
async fn get_list(
    app: Extension<Arc<AppState>>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Company>> {
    let company_service = CompanyService::new(app.pool.clone());
    match company_service.find_all(&params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Company::from).collect();
            let page_result = PageResult {
                items,
                total: result.total,
                page: result.page,
                limit: result.limit,
                total_pages: result.total_pages,
            };
            APIResponse::new().with_data(page_result)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 搜索公司
async fn search(
    app: Extension<Arc<AppState>>,
    Query(params): Query<PageParams>,
    Query(name): Query<String>,
) -> APIResponse<PageResult<Company>> {
    let company_service = CompanyService::new(app.pool.clone());
    match company_service.search_by_name(&name, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Company::from).collect();
            let page_result = PageResult {
                items,
                total: result.total,
                page: result.page,
                limit: result.limit,
                total_pages: result.total_pages,
            };
            APIResponse::new().with_data(page_result)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取公司详情
async fn get_by_id(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<Company>> {
    let company_service = CompanyService::new(app.pool.clone());
    match company_service.find_by_id(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(Company::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 删除公司
async fn delete_company(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<()> {
    let company_service = CompanyService::new(app.pool.clone());
    match company_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/insert", post(create_or_update))
        .route("/list", get(get_list))
        .route("/search", get(search))
        .route("/:id", get(get_by_id))
        .route("/:id", delete(delete_company))
}
