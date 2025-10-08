from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    app_name: str = "DDCPTS API"
    environment: str = "development"
    debug: bool = True

    # Security
    secret_key: str = "CHANGE_ME"
    access_token_exp_minutes: int = 30
    refresh_token_exp_days: int = 7
    enable_real_payments: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/ddcpts"

    # SMS
    sms_provider: str = "mock"  # mock | africastalking
    africastalking_api_key: str | None = None
    africastalking_username: str | None = None

    # Sentry
    sentry_dsn: str | None = None

    # Rate limiting (placeholder)
    rate_limit_per_minute: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
