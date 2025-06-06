use axum::Extension;
use std::error::Error;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::cors::{Any, CorsLayer};
use tracing::level_filters::LevelFilter;
use tracing_appender::{non_blocking, rolling};
use tracing_subscriber::{
    filter::EnvFilter, fmt, layer::SubscriberExt, util::SubscriberInitExt, Registry,
};

use crate::routes;
use crate::{middlewares, AppState};
use lib_utils::Settings;

pub struct Server;

impl Server {
    // 修改 run 方法签名，增加 shutdown_signal 参数
    pub async fn run(&self, config: Settings) -> Result<(), Box<dyn std::error::Error>> {
        self.setup_logging(&config)?;

        // 初始化数据库连接
        let pool = lib_core::get_db_conn(config.database_url().to_string()).await;

        // 创建应用状态
        let state = Arc::new(AppState {
            pool,
            setting: config.clone(),
        });

        // 创建路由
        let router = routes::create_router();

        let router = router.layer(middlewares::logger::LoggerLayer);

        // 在创建路由后添加 CORS 中间件
        let cors = CorsLayer::new()
            .allow_methods(Any)
            .allow_headers(Any)
            .allow_origin(Any);
        let router = router.layer(cors);

        let app = router.layer(Extension(state));

        tracing::info!("将开始在: {:?} 创建服务", config.addr);
        let listener = TcpListener::bind(config.addr).await?;

        tracing::info!("服务器启动成功，监听地址: {}", listener.local_addr()?);
        // 使用 with_graceful_shutdown
        axum::serve(listener, app.into_make_service())
            .await
            .map_err(|e| e.into())
    }

    fn setup_logging(&self, config: &Settings) -> Result<(), Box<dyn Error>> {
        let env_filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| {
            EnvFilter::builder()
                .with_default_directive(LevelFilter::INFO.into())
                .parse_lossy("")
        });

        // 输出到控制台中
        let formatting_layer = fmt::layer()
            .with_level(true)
            .pretty()
            .with_writer(std::io::stderr);

        let subscriber = Registry::default().with(env_filter).with(formatting_layer);

        // 只在配置了日志目录时添加文件日志
        if let Some(log_dir) = config.log_dir() {
            let log_file_path = format!("{}.log", chrono::Local::now().format("%Y-%m-%d"));
            let file_appender = rolling::never(log_dir, log_file_path);
            let (non_blocking_appender, _guard) = non_blocking(file_appender);
            let file_layer = fmt::layer()
                .with_ansi(false)
                .with_writer(non_blocking_appender)
                .with_span_events(fmt::format::FmtSpan::CLOSE);
            subscriber.with(file_layer).try_init()?;
        } else {
            subscriber.try_init()?;
        }

        Ok(())
    }
}
