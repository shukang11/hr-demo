use axum::{
    extract::{Path, Query},
    routing::{get, post},
    Extension, Json, Router,
};
use std::sync::Arc;

use lib_core::DepartmentService;
use lib_schema::{models::department::InsertDepartment, Department, PageParams, PageResult};

use crate::{response::APIResponse, AppState, APIError};

/// 创建或更新部门
async fn insert_department(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertDepartment>,
) -> APIResponse<Department> {
    tracing::info!("收到创建部门请求: {:?}", params);
    let department_service = DepartmentService::new(app.pool.clone());
    match department_service.insert(params).await {
        Ok(result) => {
            tracing::info!("部门创建成功: {:?}", result);
            let model = Department::from(result);
            APIResponse::new().with_data(model)
        }
        Err(e) => {
            tracing::error!("部门创建失败: {:?}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 分页查询部门列表
async fn find_by_company(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Department>> {
    let department_service = DepartmentService::new(app.pool.clone());
    match department_service.find_by_company(company_id, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Department::from).collect();
            let page_result = PageResult::new(items, result.total, &params);
            APIResponse::new().with_data(page_result)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 搜索部门
async fn search_by_name(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
    Query(name): Query<String>,
) -> APIResponse<PageResult<Department>> {
    let department_service = DepartmentService::new(app.pool.clone());
    match department_service.search_by_name(company_id, &name, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Department::from).collect();
            let page_result = PageResult::new(items, result.total, &params);
            APIResponse::new().with_data(page_result)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 查询部门详情
async fn find_by_id(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<Department>> {
    let department_service = DepartmentService::new(app.pool.clone());
    match department_service.find_by_id(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(Department::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 删除部门
async fn delete_department(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<()> {
    let department_service = DepartmentService::new(app.pool.clone());
    match department_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 构建部门路由
pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/insert", post(insert_department))
        .route("/list/:company_id", get(find_by_company))
        .route("/search/:company_id", get(search_by_name))
        .route("/get/:id", get(find_by_id))
        .route("/delete/:id", post(delete_department))
} 