pub mod services;

pub use sea_orm::DbErr;
pub type DBConnection = sea_orm::DatabaseConnection;

// Re-export commonly used types
pub use services::candidate::CandidateService;
pub use services::company::CompanyService;
pub use services::department::DepartmentService;
pub use services::employee::EmployeeService;
pub use services::position::PositionService;
pub use services::dashboard::DashboardService;

use sea_orm::{ConnectOptions, Database};
use std::time::Duration;

pub async fn get_db_conn(uri: String) -> DBConnection {
    let mut opt = ConnectOptions::new(uri.to_owned());
    opt.max_connections(1000)
        .min_connections(5)
        .connect_timeout(Duration::from_secs(30))
        .idle_timeout(Duration::from_secs(8))
        .sqlx_logging(false);
    let db = Database::connect(opt)
        .await
        .expect(format!("Failed to connect to database: {}", uri).as_str());
    println!("Database connected, {}", uri);
    tracing::info!("Database connected");
    db
}

#[cfg(test)]
mod test_runner {
    use super::DBConnection;
    use migration::{Migrator, MigratorTrait};
    use sea_orm::{EntityTrait, Set};

    pub(crate) async fn setup_database() -> DBConnection {
        let base_url =
            std::env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite::memory:?mode=rwc".to_owned());
        println!("连接数据库: {}", base_url);
        let db = crate::get_db_conn(base_url).await;
        // 假设 `Migrator` 是你的迁移模块，它实现了 `MigratorTrait`
        println!("开始运行迁移...");
        if let Err(e) = Migrator::up(&db, None).await {
            println!("迁移失败: {:?}", e);
        } else {
            println!("迁移成功");
        }
        
        // 设置基础测试数据
        println!("开始设置基础测试数据...");
        if let Err(e) = setup_test_data(&db).await {
            println!("设置测试数据失败: {:?}", e);
        } else {
            println!("测试数据设置成功");
        }
        
        db
    }
    
    /// 创建测试所需的基础数据
    async fn setup_test_data(db: &DBConnection) -> Result<(), sea_orm::DbErr> {
        use lib_entity::entities::{company, department, position, employee};
        
        // 创建测试公司
        let company_data = company::ActiveModel {
            id: Set(1),
            name: Set("测试公司".to_string()),
            extra_value: Set(None),
            extra_schema_id: Set(None),
            ..Default::default()
        };
        company::Entity::insert(company_data).exec(db).await?;
        
        // 创建测试部门
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
        
        // 创建测试职位
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
        
        // 创建测试员工（可以作为部门负责人）
        let employee_data = employee::ActiveModel {
            id: Set(1),
            company_id: Set(1),
            name: Set("测试员工".to_string()),
            email: Set(Some("test@example.com".to_string())),
            phone: Set(Some("13800000000".to_string())),
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
        
        Ok(())
    }
}
