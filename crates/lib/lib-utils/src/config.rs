use std::net::SocketAddr;
use once_cell::sync::OnceCell;
use serde::{Deserialize, Serialize};
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
pub struct Settings {
    pub addr: SocketAddr,
    pub log_dir: Option<String>,
    pub database_url: String,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            addr: "127.0.0.1:3000".parse().unwrap(),
            log_dir: None,
            database_url: "sqlite:memory:".to_string(),
        }
    }
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

    pub fn with_addr(mut self, addr: impl AsRef<str>) -> Self {
        self.addr = addr.as_ref().parse().expect("Invalid address format");
        self
    }

    pub fn with_database_url(mut self, database_url: impl Into<String>) -> Self {
        self.database_url = database_url.into();
        self
    }

    pub fn with_log_dir(mut self, dir: impl Into<String>) -> Self {
        self.log_dir = Some(dir.into());
        self
    }

    pub fn addr(&self) -> SocketAddr {
        self.addr
    }

    pub fn log_dir(&self) -> Option<&str> {
        self.log_dir.as_deref()
    }

    pub fn database_url(&self) -> &str {
        &self.database_url
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_config() {
        let config = Settings::default()
            .with_addr("127.0.0.1:8080")
            .with_database_url("sqlite:test.db")
            .with_log_dir("logs");

        assert_eq!(config.addr().port(), 8080);
        assert_eq!(config.database_url(), "sqlite:test.db");
        assert_eq!(config.log_dir(), Some("logs"));
    }
}