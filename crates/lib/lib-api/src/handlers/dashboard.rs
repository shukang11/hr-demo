use axum::{
    extract::{Path, Query},
    routing::get,
    Extension, Router,
};
use lib_core::DashboardService;
use lib_schema::models::dashboard::*;
use std::sync::Arc;

use crate::{response::APIResponse, APIError, AppState};

/// 获取公司人员概览统计数据
async fn get_employee_overview(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(date_range): Query<DateRange>,
) -> APIResponse<EmployeeOverview> {
    tracing::info!("收到获取公司人员概览统计数据请求: company_id={}", company_id);
    let dashboard_service = DashboardService::new(app.pool.clone());
    match dashboard_service.get_employee_overview(company_id, &date_range).await {
        Ok(stats) => {
            tracing::info!("获取公司人员概览统计数据成功");
            APIResponse::new().with_data(stats)
        }
        Err(e) => {
            tracing::error!("获取公司人员概览统计数据失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取公司招聘概况统计数据
async fn get_recruitment_stats(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(date_range): Query<DateRange>,
) -> APIResponse<RecruitmentStats> {
    tracing::info!("收到获取公司招聘概况统计数据请求: company_id={}", company_id);
    let dashboard_service = DashboardService::new(app.pool.clone());
    match dashboard_service.get_recruitment_stats(company_id, &date_range).await {
        Ok(stats) => {
            tracing::info!("获取公司招聘概况统计数据成功");
            APIResponse::new().with_data(stats)
        }
        Err(e) => {
            tracing::error!("获取公司招聘概况统计数据失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取公司组织发展统计数据
async fn get_organization_stats(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(date_range): Query<DateRange>,
) -> APIResponse<OrganizationStats> {
    tracing::info!("收到获取公司组织发展统计数据请求: company_id={}", company_id);
    let dashboard_service = DashboardService::new(app.pool.clone());
    match dashboard_service.get_organization_stats(company_id, &date_range).await {
        Ok(stats) => {
            tracing::info!("获取公司组织发展统计数据成功");
            APIResponse::new().with_data(stats)
        }
        Err(e) => {
            tracing::error!("获取公司组织发展统计数据失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取公司完整看板统计数据
async fn get_company_stats(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(date_range): Query<DateRange>,
) -> APIResponse<DashboardStats> {
    tracing::info!("收到获取公司完整看板统计数据请求: company_id={}", company_id);
    let dashboard_service = DashboardService::new(app.pool.clone());
    match dashboard_service.get_stats(company_id, &date_range).await {
        Ok(stats) => {
            tracing::info!("获取公司完整看板统计数据成功");
            APIResponse::new().with_data(stats)
        }
        Err(e) => {
            tracing::error!("获取公司完整看板统计数据失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

/// 获取指定时间范围内过生日的员工列表
async fn get_birthday_employees(
    app: Extension<Arc<AppState>>,
    Path(company_id): Path<i32>,
    Query(date_range): Query<DateRange>,
) -> APIResponse<Vec<BirthdayEmployee>> {
    tracing::info!("收到获取生日员工列表请求: company_id={}, date_range={:?}", company_id, date_range);
    
    let dashboard_service = DashboardService::new(app.pool.clone());
    match dashboard_service.get_birthday_employees(company_id, &date_range).await {
        Ok(employees) => {
            tracing::info!("获取生日员工列表成功");
            APIResponse::new().with_data(employees)
        }
        Err(e) => {
            tracing::error!("获取生日员工列表失败: {}", e);
            APIError::Internal(e.into()).into()
        }
    }
}

pub(crate) fn build_routes() -> Router {
    Router::new()
        .route("/stats/:company_id", get(get_company_stats))
        .route("/employee-overview/:company_id", get(get_employee_overview))
        .route("/recruitment-stats/:company_id", get(get_recruitment_stats))
        .route("/organization-stats/:company_id", get(get_organization_stats))
        .route("/birthday-employees/:company_id", get(get_birthday_employees))
} 