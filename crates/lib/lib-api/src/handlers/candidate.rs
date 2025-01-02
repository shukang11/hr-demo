use axum::{
    extract::{Path, Query},
    routing::{get, post},
    Extension, Json, Router,
};
use lib_core::CandidateService;
use lib_schema::{
    models::candidate::UpdateCandidateStatus,
    Candidate, InsertCandidate, PageParams, PageResult,
};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 创建或更新候选人
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertCandidate>,
) -> APIResponse<Candidate> {
    let candidate_service = CandidateService::new(app.pool.clone());
    match candidate_service.create(params).await {
        Ok(result) => {
            let model = Candidate::from(result);
            tracing::info!("创建候选人成功: id={}", model.id);
            APIResponse::new().with_data(model)
        }
        Err(e) => {
            tracing::error!("创建候选人失败: {}", e);
            if e.to_string().contains("同一天内已存在相同姓名的候选人") {
                APIError::BadRequest(e.to_string()).into()
            } else {
                APIError::Internal(e.into()).into()
            }
        }
    }
}

/// 更新候选人状态
async fn update_status(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
    Json(params): Json<UpdateCandidateStatus>,
) -> APIResponse<Candidate> {
    let candidate_service = CandidateService::new(app.pool.clone());
    let status = params.status.clone();
    match candidate_service
        .update_status(id, params)
        .await
    {
        Ok(result) => {
            let model = Candidate::from(result);
            tracing::info!("更新候选人状态成功: id={}, status={:?}", id, status);
            APIResponse::new().with_data(model)
        }
        Err(e) => {
            tracing::error!("更新候选人状态失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取候选人列表
async fn get_list(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Candidate>> {
    let candidate_service = CandidateService::new(app.pool.clone());
    match candidate_service.find_all(company_id).await {
        Ok(list) => {
            let total = list.len() as u64;
            let items = list.into_iter().map(Candidate::from).collect();
            let page_result = PageResult {
                items,
                total,
                page: params.page,
                limit: params.limit,
                total_pages: ((total as f64) / (params.limit as f64)).ceil() as u64,
            };
            APIResponse::new().with_data(page_result)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取候选人详情
async fn get_by_id(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<Candidate>> {
    let candidate_service = CandidateService::new(app.pool.clone());
    match candidate_service.find_by_id(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(Candidate::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 删除候选人
async fn delete_candidate(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<()> {
    let candidate_service = CandidateService::new(app.pool.clone());
    match candidate_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 构建路由
pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/insert", post(create_or_update))
        .route("/:id/status", post(update_status))
        .route("/list/:company_id", get(get_list))
        .route("/get/:id", get(get_by_id))
        .route("/delete/:id", post(delete_candidate))
} 