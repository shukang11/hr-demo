use axum::{
    extract::{Path, Query},
    routing::{get, post},
    Extension, Json, Router,
};
use lib_core::EmployeeService;
use lib_schema::{
    models::{
        employee::InsertEmployee,
        employee_position::{EmployeePosition, InsertEmployeePosition},
    },
    Employee, PageParams, PageResult,
};
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 创建或更新雇员
async fn create_or_update(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertEmployee>,
) -> APIResponse<Employee> {
    tracing::info!(
        "收到创建雇员请求: company_id={}, name={}, phone={:?}, email={:?}",
        params.company_id, params.name, params.phone, params.email
    );

    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.insert(params).await {
        Ok(result) => {
            tracing::info!("创建雇员成功: id={}", result.id);
            APIResponse::new().with_data(result)
        }
        Err(e) => {
            tracing::error!("创建雇员失败: {}", e);
            if e.to_string().contains("该公司已存在相同手机号或邮箱的员工") {
                tracing::warn!("尝试创建重复的员工");
                APIError::BadRequest(e.to_string()).into()
            } else {
                APIError::Internal(e.into()).into()
            }
        }
    }
}

/// 获取雇员列表
async fn get_list(
    app: Extension<Arc<AppState>>,
    Query(params): Query<PageParams>,
) -> APIResponse<PageResult<Employee>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_all(&params).await {
        Ok(result) => APIResponse::new().with_data(result),
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
        Ok(result) => APIResponse::new().with_data(result),
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
    match employee_service
        .find_by_department(department_id, &params)
        .await
    {
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
async fn delete_employee(app: Extension<Arc<AppState>>, Path(id): Path<i32>) -> APIResponse<()> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.delete(id).await {
        Ok(_) => APIResponse::new(),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 为员工加职位
async fn add_position(
    app: Extension<Arc<AppState>>,
    Json(params): Json<InsertEmployeePosition>,
) -> APIResponse<EmployeePosition> {
    tracing::info!("收到添加职位请求: {:?}", params);
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.add_position(params).await {
        Ok(result) => {
            let model = EmployeePosition::from(result);
            tracing::info!("添加职位成功: id={}", model.id);
            APIResponse::new().with_data(model)
        }
        Err(e) => {
            tracing::error!("添加职位失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 移除员工职位
async fn remove_position(app: Extension<Arc<AppState>>, Path(id): Path<i32>) -> APIResponse<()> {
    tracing::info!("收到移除职位请求: id={}", id);
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.remove_position(id).await {
        Ok(_) => {
            tracing::info!("移除职位成功: id={}", id);
            APIResponse::new()
        }
        Err(e) => {
            tracing::error!("移除职位失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取员工的职位列表
async fn get_employee_positions(
    app: Extension<Arc<AppState>>,
    Path(employee_id): Path<i32>,
) -> APIResponse<Vec<EmployeePosition>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service
        .find_positions_by_employee(employee_id)
        .await
    {
        Ok(result) => {
            let positions = result.into_iter().map(EmployeePosition::from).collect();
            APIResponse::new().with_data(positions)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取员工当前职位状态
async fn get_current_position(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Option<EmployeePosition>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_current_position(id).await {
        Ok(result) => APIResponse::new().with_data(result.map(EmployeePosition::from)),
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

/// 获取员工所有职位历史
async fn get_position_history(
    app: Extension<Arc<AppState>>,
    Path(id): Path<i32>,
) -> APIResponse<Vec<EmployeePosition>> {
    let employee_service = EmployeeService::new(app.pool.clone());
    match employee_service.find_positions_by_employee(id).await {
        Ok(result) => {
            let items = result.into_iter().map(EmployeePosition::from).collect();
            APIResponse::new().with_data(items)
        }
        Err(e) => APIError::Internal(e.into()).into(),
    }
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/insert", post(create_or_update))
        .route("/list", get(get_list))
        .route("/list/:company_id", get(get_list_by_company))
        .route(
            "/list/department/:department_id",
            get(get_list_by_department),
        )
        .route("/search", get(search))
        .route("/get/:id", get(get_by_id))
        .route("/delete/:id", post(delete_employee))
        .route("/position/add", post(add_position))
        .route("/position/remove/:id", post(remove_position))
        .route("/position/list/:employee_id", get(get_employee_positions))
        .route("/position/:id", get(get_current_position))
        .route("/position/history/:id", get(get_position_history))
}
