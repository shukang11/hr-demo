use lib_api::{Server, Settings};
use tokio::runtime::Runtime;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 创建一个新的 Tokio 运行时
    let runtime = Runtime::new().expect("无法创建 Tokio 运行时");
    // 进入运行时上下文，以便 tracing 初始化可以工作
    let _guard = runtime.enter();

    // 这里需要首先读取配置项目,用来指定项目的工作区目录

    // 使用创建的运行时来 spawn 后台服务任务
    runtime.spawn(async move {
        // 注意这里的 move
        // 初始化配置
        let config = Settings::default()
            .with_log_dir("./data/tauri-logs")
            .with_database_url("sqlite://./data/hr-data-tauri.sqlite3?mode=rwc");

        // 创建服务器实例
        let server = Server;
        // 启动服务器
        if let Err(e) = server.run(config).await {
            eprintln!("启动 API 服务失败: {}", e);
        } else {
            // 确保在 server.run 成功返回后（即服务器已关闭）打印日志
            eprintln!("API 服务已成功关闭。");
        }
    });

    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet]);

    // 启动 Tauri 应用
    builder
        .run(tauri::generate_context!())
        .expect("运行 Tauri 应用时出错");

    // Tauri run 返回后，意味着所有窗口已关闭
    println!("Tauri 应用退出，开始关闭 Tokio 运行时...");
    // 关闭 Tokio 运行时，给后台任务一些时间完成
    runtime.shutdown_background(); // 立即开始关闭，不阻塞
    println!("Tokio 运行时已关闭。");
}
