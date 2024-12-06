use sqlx::SqlitePool;
use std::sync::Arc;
use anyhow::Result;

/// 数据库连接池类型
pub type DBPool = Arc<SqlitePool>;

/// 创建数据库连接池
pub async fn create_pool(database_url: &str) -> Result<DBPool> {
    let pool = SqlitePool::connect(database_url).await?;
    Ok(Arc::new(pool))
}

/// 关闭数据库连接池
pub async fn close_pool(pool: DBPool) {
    pool.close().await;
} 