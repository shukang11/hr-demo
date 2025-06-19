use chrono::{NaiveDateTime, Utc};
use lib_core::services::candidate::CandidateService;
use lib_entity::entities::candidate::CandidateStatus;
use lib_schema::models::candidate::{InsertCandidate, UpdateCandidateStatus};
use pretty_assertions::assert_eq;
use sea_orm::DatabaseConnection;

use crate::common;

/// 获取测试数据库连接
async fn get_db() -> DatabaseConnection {
    common::create_test_db()
        .await
        .expect("Failed to create test database")
}

/// 创建候选人服务实例
fn create_service(db: DatabaseConnection) -> CandidateService {
    CandidateService::new(db)
}

#[tokio::test]
async fn test_create_candidate_success() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    let result = service.create(candidate_data.clone()).await;

    if let Err(ref e) = result {
        println!("创建候选人失败: {:?}", e);
    }
    assert!(result.is_ok(), "创建候选人应该成功");

    let created_candidate = result.unwrap();
    assert_eq!(created_candidate.name, candidate_data.name);
    assert_eq!(created_candidate.phone, candidate_data.phone);
    assert_eq!(created_candidate.email, candidate_data.email);
    assert_eq!(created_candidate.position_id, candidate_data.position_id);
    assert_eq!(
        created_candidate.department_id,
        candidate_data.department_id
    );
    assert_eq!(created_candidate.status, CandidateStatus::Pending);
}

#[tokio::test]
async fn test_create_duplicate_candidate_same_day() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    // 第一次创建应该成功
    let first_result = service.create(candidate_data.clone()).await;
    assert!(first_result.is_ok(), "第一次创建候选人应该成功");

    // 同一天创建相同姓名的候选人应该失败
    let duplicate_data = InsertCandidate {
        name: candidate_data.name.clone(),
        phone: candidate_data.phone.clone(),
        email: candidate_data.email.clone(),
        interview_date: candidate_data.interview_date,
        ..candidate_data
    };

    let second_result = service.create(duplicate_data).await;
    assert!(second_result.is_err(), "同一天创建相同姓名的候选人应该失败");

    let error_msg = second_result.err().unwrap().to_string();
    assert!(error_msg.contains("同一天内已存在相同姓名的候选人"));
}

#[tokio::test]
async fn test_find_by_id_success() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    // 先创建一个候选人
    let created = service.create(candidate_data).await.unwrap();

    // 根据ID查找
    let found = service.find_by_id(created.id).await.unwrap();

    assert!(found.is_some(), "应该能找到创建的候选人");
    let found_candidate = found.unwrap();
    assert_eq!(found_candidate.id, created.id);
    assert_eq!(found_candidate.name, created.name);
}

#[tokio::test]
async fn test_find_by_id_not_found() {
    let db = get_db().await;
    let service = create_service(db);

    // 查找不存在的ID
    let result = service.find_by_id(99999).await.unwrap();
    assert!(result.is_none(), "不存在的ID应该返回None");
}

#[tokio::test]
async fn test_find_all_candidates() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate1 = common::create_test_candidate_data();
    let mut candidate2 = common::create_test_candidate_data_2();

    // 设置不同的面试时间以避免重复检查
    candidate2.interview_date = Some(Utc::now().naive_utc() + chrono::Duration::hours(1));

    // 创建两个候选人
    service.create(candidate1).await.unwrap();
    service.create(candidate2).await.unwrap();

    // 查找所有候选人
    let all_candidates = service.find_all(1).await.unwrap();

    assert!(all_candidates.len() >= 2, "应该至少有2个候选人");
}

#[tokio::test]
async fn test_update_candidate_status() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    // 创建候选人
    let created = service.create(candidate_data).await.unwrap();
    assert_eq!(created.status, CandidateStatus::Pending);

    // 更新状态
    let status_update = UpdateCandidateStatus {
        status: CandidateStatus::Interviewed,
        evaluation: Some("面试表现良好".to_string()),
        remark: Some("技术能力符合要求".to_string()),
    };

    let updated = service
        .update_status(created.id, status_update.clone())
        .await
        .unwrap();

    assert_eq!(updated.status, CandidateStatus::Interviewed);
    assert_eq!(updated.evaluation, status_update.evaluation);
    assert_eq!(updated.remark, status_update.remark);
}

#[tokio::test]
async fn test_update_nonexistent_candidate_status() {
    let db = get_db().await;
    let service = create_service(db);

    let status_update = UpdateCandidateStatus {
        status: CandidateStatus::Accepted,
        evaluation: None,
        remark: None,
    };

    let result = service.update_status(99999, status_update).await;

    assert!(result.is_err(), "更新不存在的候选人状态应该失败");
    let error_msg = result.err().unwrap().to_string();
    assert!(error_msg.contains("Candidate not found"));
}

#[tokio::test]
async fn test_delete_candidate() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    // 创建候选人
    let created = service.create(candidate_data).await.unwrap();

    // 删除候选人
    let delete_result = service.delete(created.id).await.unwrap();
    assert_eq!(delete_result.rows_affected, 1);

    // 验证已删除
    let found = service.find_by_id(created.id).await.unwrap();
    assert!(found.is_none(), "删除后应该找不到候选人");
}

#[tokio::test]
async fn test_delete_nonexistent_candidate() {
    let db = get_db().await;
    let service = create_service(db);

    // 删除不存在的候选人
    let delete_result = service.delete(99999).await.unwrap();
    assert_eq!(
        delete_result.rows_affected, 0,
        "删除不存在的候选人应该影响0行"
    );
}

#[tokio::test]
async fn test_candidate_status_flow() {
    let db = get_db().await;
    let service = create_service(db);

    let candidate_data = common::create_test_candidate_data();

    // 创建候选人 (默认状态为Pending)
    let created = service.create(candidate_data).await.unwrap();
    assert_eq!(created.status, CandidateStatus::Pending);

    // 1. 更新为已安排面试
    let scheduled_update = UpdateCandidateStatus {
        status: CandidateStatus::Scheduled,
        evaluation: None,
        remark: Some("已安排下周二面试".to_string()),
    };
    let scheduled = service
        .update_status(created.id, scheduled_update)
        .await
        .unwrap();
    assert_eq!(scheduled.status, CandidateStatus::Scheduled);

    // 2. 更新为已面试
    let interviewed_update = UpdateCandidateStatus {
        status: CandidateStatus::Interviewed,
        evaluation: Some("技术能力强，沟通良好".to_string()),
        remark: Some("推荐录用".to_string()),
    };
    let interviewed = service
        .update_status(created.id, interviewed_update)
        .await
        .unwrap();
    assert_eq!(interviewed.status, CandidateStatus::Interviewed);
    assert!(interviewed.evaluation.is_some());

    // 3. 最终录用
    let accepted_update = UpdateCandidateStatus {
        status: CandidateStatus::Accepted,
        evaluation: interviewed.evaluation.clone(),
        remark: Some("已发送录用通知".to_string()),
    };
    let accepted = service
        .update_status(created.id, accepted_update)
        .await
        .unwrap();
    assert_eq!(accepted.status, CandidateStatus::Accepted);
}

#[tokio::test]
async fn test_candidate_with_extra_fields() {
    let db = get_db().await;
    let service = create_service(db);

    let extra_value = serde_json::json!({
        "years_of_experience": 5,
        "skills": ["Rust", "Python", "JavaScript"],
        "education": "Master's Degree"
    });    let candidate_data = InsertCandidate {
        extra_value: Some(extra_value.clone()),
        extra_schema_id: None, // 不使用 schema ID 以避免外键约束
        ..common::create_test_candidate_data()
    };

    let created = service.create(candidate_data).await.unwrap();

    assert_eq!(created.extra_value, Some(extra_value));
    assert_eq!(created.extra_schema_id, None);

    // 验证从数据库重新获取的数据一致
    let found = service.find_by_id(created.id).await.unwrap().unwrap();
    assert_eq!(found.extra_value, created.extra_value);
    assert_eq!(found.extra_schema_id, created.extra_schema_id);
}
