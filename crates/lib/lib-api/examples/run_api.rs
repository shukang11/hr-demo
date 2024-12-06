use lib_api::Server;
use lib_utils::Settings;

#[tokio::main]
async fn main() {
    // 初始化配置
    let config = Settings::init().unwrap().to_owned();
    // 创建服务器实例
    let server = Server;
    // 启动服务器
    server.run(config).await.unwrap();
} 