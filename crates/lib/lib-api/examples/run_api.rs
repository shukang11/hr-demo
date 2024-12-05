use lib_api::{Server, Config};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 创建配置
    let config = Config::default()
        .with_database_url("sqlite:data.sqlite")
        .with_addr("127.0.0.1:3000");
    
    // 创建服务器实例
    let server = Server;
    
    // 运行服务器
    println!("正在启动服务器...");
    server.run(config).await?;
    
    Ok(())
}
