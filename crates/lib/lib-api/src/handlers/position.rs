use axum::{
    extract::{Path, Query},
    routing::{get, post},
    Extension, Json, Router,
};
use lib_core::PositionService;
use lib_schema::{models::position::InsertPosition, Position, PageParams, PageResult};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 创建或更新职位
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertPosition>,
) -> APIResponse<Position> {
    let position_service = PositionService::new(app.pool.clone());
    match position_service.insert(params).await {
        Ok(result) => {
            let model = Position::from(result);
            APIResponse::new().with_data(model)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取职位列表
async fn get_list(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Position>> {
    let position_service = PositionService::new(app.pool.clone());
    match position_service.find_by_company(company_id, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Position::from).collect();
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

/// 搜索职位
async fn search(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
    Query(name): Query<String>,
) -> APIResponse<PageResult<Position>> {
    let position_service = PositionService::new(app.pool.clone());
    match position_service.search_by_name(company_id, &name, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Position::from).collect();
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

/// 获取职位详情
async fn get_by_id(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<Position>> {
    let position_service = PositionService::new(app.pool.clone());
    match position_service.find_by_id(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(Position::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 删除职位
async fn delete_position(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<()> {
    let position_service = PositionService::new(app.pool.clone());
    match position_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/create", post(create_or_update))
        .route("/list/:company_id", get(get_list))
        .route("/search/:company_id", get(search))
        .route("/get/:id", get(get_by_id))
        .route("/delete/:id", post(delete_position))
} 