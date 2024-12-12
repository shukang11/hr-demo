use axum::{
    extract::{Path, Query, State}, routing::{get, post}, Extension, Json, Router
};
use lib_core::CompanyService;
use lib_schema::{
    models::company::InsertCompany, Company, PageParams, PageResult
};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

#[utoipa::path(
    post,
    path = "/",
    tag = "company",
    request_body = InsertCompany,
    responses(
        (status = 200, description = "创建或更新公司成功", body = APIResponse<Company>)
    )
)]
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertCompany>,
) -> Result<APIResponse<Company>, APIError> {
    let company_service = CompanyService::new(app.pool.clone());
    let result = company_service.insert(params).await.map_err(|e| APIError::Internal(e.into()))?;
    Ok(APIResponse::new(result))
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/", post(create_or_update))
        // .route("/", get(get_list))
        // .route("/search", get(search))
        // .route("/:id", get(get_by_id))
        // .route("/:id", delete(delete))
}