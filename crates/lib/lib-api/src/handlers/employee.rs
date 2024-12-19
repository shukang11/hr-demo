use axum::{
    extract::{Path, Query},
    routing::{get, post, delete},
    Extension, Json, Router,
};
use lib_core::EmployeeService;
use lib_schema::{models::employee::InsertEmployee, Employee, PageParams, PageResult};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 创建或更新雇员
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertEmployee>,
) -> APIResponse<Employee> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.insert(params).await {
        Ok(result) => {
            let model = Employee::from(result);
            APIResponse::new().with_data(model)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取雇员列表
async fn get_list(
    app: Extension<Arc<AppState>>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_all(&params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Employee::from).collect();
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

/// 按公司查询雇员列表
async fn get_list_by_company(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_by_company(company_id, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Employee::from).collect();
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

/// 按部门查询雇员列表
async fn get_list_by_department(
    app: Extension<Arc<AppState>>,
    Path(department_id): Path<i32>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_by_department(department_id, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Employee::from).collect();
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

/// 搜索雇员
async fn search(
    app: Extension<Arc<AppState>>,
    Query(params): Query<PageParams>,
    Query(name): Query<String>,
) -> APIResponse<PageResult<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.search_by_name(&name, &params).await {
        Ok(result) => {
            let items = result.items.into_iter().map(Employee::from).collect();
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

/// 获取雇员详情
async fn get_by_id(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_by_id(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(Employee::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 删除雇员
async fn delete_employee(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<()> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/insert", post(create_or_update))
        .route("/list", get(get_list))
        .route("/list/:company_id", get(get_list_by_company))
        .route("/list/department/:department_id", get(get_list_by_department))
        .route("/search", get(search))
        .route("/get/:id", get(get_by_id))
        .route("/delete/:id", post(delete_employee))
} 