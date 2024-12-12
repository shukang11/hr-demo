from pydantic_settings import SettingsConfigDict

from .feature import FeatureConfig
from .deploy import DeploymentConfig
from ._database import DatabaseConfig


class AppConfig(
    # Deployment configs
    DeploymentConfig,
    # Feature configs
    FeatureConfig,
    DatabaseConfig,
):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )