from pydantic import Field
from pydantic_settings import BaseSettings
from libs.helper import get_sha256

class DeploymentConfig(BaseSettings):
    """
    Configuration settings for application deployment
    """

    APPLICATION_NAME: str = Field(
        description="Name of the application, used for identification and logging purposes",
        default="home-app/api",
    )

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=True,
    )

    TESTING: bool = Field(
        description="Enable testing mode for running automated tests", default=False
    )

    AUTO_MIGRATE_DB: bool = Field(
        description="Automatically run database migrations on startup in development mode",
        default=True,
    )

    SECRET_KEY: str = Field(
        description="Secret key for signing cookies and other cryptographic operations",
        default_factory=lambda: get_sha256("random_secret_key"),
    )