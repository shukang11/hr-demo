use once_cell::sync::OnceCell;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use thiserror::Error;

static CONFIG: OnceCell<Settings> = OnceCell::new();

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("配置加载失败: {0}")]
    LoadError(#[from] config::ConfigError),
    #[error("配置未初始化")]
    NotInitialized,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Settings {
    pub workspace: PathBuf,
    pub database: DatabaseConfig,
    pub server: ServerConfig,
}

impl Settings {
    pub fn init() -> Result<&'static Settings, ConfigError> {
        let config = config::Config::builder()
            .add_source(config::File::with_name("config/default"))
            .add_source(config::Environment::with_prefix("APP"))
            .build()?
            .try_deserialize()?;

        CONFIG.set(config).unwrap();
        Ok(CONFIG.get().unwrap())
    }

    pub fn get() -> Result<&'static Settings, ConfigError> {
        CONFIG.get().ok_or(ConfigError::NotInitialized)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_config() {
        // 这里需要确保测试环境中存在配置文件
        let config = Settings::init().expect("Failed to load config");
        assert!(config.workspace.exists());
        assert!(config.server.port > 0);
    }
} 