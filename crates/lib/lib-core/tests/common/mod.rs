use migration::{Migrator, MigratorTrait};
use sea_orm::{Database, DatabaseConnection, DbErr, ConnectionTrait};
use std::sync::Arc;
use tokio::sync::Mutex;

/// 测试数据库连接池
static TEST_DB: Mutex<Option<Arc<DatabaseConnection>>> = Mutex::const_new(None);

/// 获取测试数据库连接（共享实例）
pub async fn get_test_db() -> Result<DatabaseConnection, DbErr> {
    let mut db_guard = TEST_DB.lock().await;

    if let Some(db) = db_guard.as_ref() {
        return Ok((**db).clone());
    }

    // 使用内存SQLite数据库进行测试
    let db = Database::connect("sqlite::memory:").await?;

    println!("Database connected, {:?}", db.get_database_backend());

    // 运行迁移
    match Migrator::up(&db, None).await {
        Ok(_) => println!("Migration successful"),
        Err(e) => {
            println!("Migration failed: {:?}", e);
            return Err(e);
        }
    }

    // 设置基础测试数据
    match setup_test_data(&db).await {
        Ok(_) => println!("Test data setup successful"),
        Err(e) => {
            println!("Test data setup failed: {:?}", e);
            return Err(e);
        }
    }

    let db_arc = Arc::new(db);
    *db_guard = Some(db_arc.clone());

    Ok((*db_arc).clone())
}

/// 为每个测试创建独立的数据库连接
pub async fn create_test_db() -> Result<DatabaseConnection, DbErr> {
    // 使用独立的内存SQLite数据库进行测试
    let db = Database::connect("sqlite::memory:").await?;

    // 运行迁移
    Migrator::up(&db, None).await?;

    // 设置基础测试数据
    setup_test_data(&db).await?;

    Ok(db)
}

/// 清理测试数据库（可选，用于特定测试）
pub async fn cleanup_test_db() -> Result<(), DbErr> {
    let mut db_guard = TEST_DB.lock().await;
    if let Some(db) = db_guard.as_ref() {
        // 执行清理操作，例如删除所有数据
        // 这里可以根据需要添加具体的清理逻辑
        let _ = db;
    }
    *db_guard = None;
    Ok(())
}

/// 创建测试候选人数据的辅助函数
pub fn create_test_candidate_data() -> lib_schema::models::candidate::InsertCandidate {
    lib_schema::models::candidate::InsertCandidate {
        id: None,
        company_id: 1,
        name: "张三".to_string(),
        phone: Some("13800138000".to_string()),
        email: Some("zhangsan@example.com".to_string()),
        position_id: 1,
        department_id: 1,
        interview_date: Some(chrono::Utc::now().naive_utc()),
        interviewer_id: Some(1),
        extra_value: None,
        extra_schema_id: None,
    }
}

/// 创建另一个测试候选人数据
pub fn create_test_candidate_data_2() -> lib_schema::models::candidate::InsertCandidate {
    lib_schema::models::candidate::InsertCandidate {
        id: None,
        company_id: 1,
        name: "李四".to_string(),
        phone: Some("13900139000".to_string()),
        email: Some("lisi@example.com".to_string()),
        position_id: 2,
        department_id: 2,
        interview_date: Some(chrono::Utc::now().naive_utc()),
        interviewer_id: Some(2),
        extra_value: None,
        extra_schema_id: None,
    }
}

/// 创建测试所需的基础数据（公司、部门、职位等）
pub async fn setup_test_data(db: &DatabaseConnection) -> Result<(), DbErr> {
    use lib_entity::entities::{company, department, position, employee};
    use sea_orm::{EntityTrait, Set};
    
    // 1. 创建测试公司
    let company_data = company::ActiveModel {
        id: Set(1),
        name: Set("测试公司".to_string()),
        extra_value: Set(None),
        extra_schema_id: Set(None),
        ..Default::default()
    };
    company::Entity::insert(company_data).exec(db).await?;
    
    // 2. 创建测试部门
    let department_data = department::ActiveModel {
        id: Set(1),
        company_id: Set(1),
        parent_id: Set(None),
        name: Set("技术部".to_string()),
        leader_id: Set(None),
        remark: Set(None),
        ..Default::default()
    };
    department::Entity::insert(department_data).exec(db).await?;
    
    let department_data2 = department::ActiveModel {
        id: Set(2),
        company_id: Set(1),
        parent_id: Set(None),
        name: Set("人事部".to_string()),
        leader_id: Set(None),
        remark: Set(None),
        ..Default::default()
    };
    department::Entity::insert(department_data2).exec(db).await?;
    
    // 3. 创建测试职位
    let position_data = position::ActiveModel {
        id: Set(1),
        company_id: Set(1),
        name: Set("软件工程师".to_string()),
        remark: Set(None),
        ..Default::default()
    };
    position::Entity::insert(position_data).exec(db).await?;
    
    let position_data2 = position::ActiveModel {
        id: Set(2),
        company_id: Set(1),
        name: Set("产品经理".to_string()),
        remark: Set(None),
        ..Default::default()
    };
    position::Entity::insert(position_data2).exec(db).await?;
      // 4. 创建测试员工（作为面试官）
    let employee_data = employee::ActiveModel {
        id: Set(1),
        company_id: Set(1),
        name: Set("张面试官".to_string()),
        email: Set(Some("interviewer1@test.com".to_string())),
        phone: Set(Some("18800000001".to_string())),
        birthdate: Set(None),
        address: Set(None),
        gender: Set(employee::Gender::Male),
        extra_value: Set(None),
        extra_schema_id: Set(None),
        marital_status: Set(None),
        emergency_contact: Set(None),
        ..Default::default()
    };
    employee::Entity::insert(employee_data).exec(db).await?;
    
    let employee_data2 = employee::ActiveModel {
        id: Set(2),
        company_id: Set(1),
        name: Set("李面试官".to_string()),
        email: Set(Some("interviewer2@test.com".to_string())),
        phone: Set(Some("18800000002".to_string())),
        birthdate: Set(None),
        address: Set(None),
        gender: Set(employee::Gender::Female),
        extra_value: Set(None),
        extra_schema_id: Set(None),
        marital_status: Set(None),
        emergency_contact: Set(None),
        ..Default::default()
    };
    employee::Entity::insert(employee_data2).exec(db).await?;
    
    Ok(())
}
