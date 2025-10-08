"""
Application configuration management.

Loads configuration from environment variables using Pydantic settings.
All sensitive values should be provided via environment variables.
"""

from typing import List, Optional
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    See .env.example for a complete list of configuration options.
    """
    
    # ============================================
    # APPLICATION
    # ============================================
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_WORKERS: int = Field(default=4)
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://ddcpts:ddcpts_dev_password@localhost:5432/ddcpts_dev"
    )
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=3600)
    
    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.DATABASE_URL)
    
    # ============================================
    # SECURITY & AUTHENTICATION
    # ============================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT signing (use: openssl rand -hex 32)"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Password policy
    MIN_PASSWORD_LENGTH: int = Field(default=8)
    REQUIRE_PASSWORD_UPPERCASE: bool = Field(default=True)
    REQUIRE_PASSWORD_LOWERCASE: bool = Field(default=True)
    REQUIRE_PASSWORD_DIGIT: bool = Field(default=True)
    REQUIRE_PASSWORD_SPECIAL_CHAR: bool = Field(default=True)
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_AUTH_PER_MINUTE: int = Field(default=10)
    
    # ============================================
    # SMS PROVIDER
    # ============================================
    SMS_PROVIDER: str = Field(default="mock", description="SMS provider: africastalking, twilio, mock")
    
    # Africa's Talking
    AFRICASTALKING_USERNAME: str = Field(default="sandbox")
    AFRICASTALKING_API_KEY: str = Field(default="")
    AFRICASTALKING_SENDER_ID: str = Field(default="DDCPTS")
    AFRICASTALKING_ENVIRONMENT: str = Field(default="sandbox")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(default="")
    TWILIO_AUTH_TOKEN: str = Field(default="")
    TWILIO_PHONE_NUMBER: str = Field(default="")
    
    # SMS Configuration
    SMS_RETRY_ATTEMPTS: int = Field(default=3)
    SMS_RETRY_DELAY_SECONDS: int = Field(default=60)
    SMS_MAX_LENGTH: int = Field(default=160)
    
    # ============================================
    # PAYMENT PROVIDER (M-Pesa Daraja)
    # ============================================
    MPESA_ENVIRONMENT: str = Field(default="sandbox", description="sandbox or production")
    MPESA_CONSUMER_KEY: str = Field(default="")
    MPESA_CONSUMER_SECRET: str = Field(default="")
    MPESA_SHORTCODE: str = Field(default="174379")
    MPESA_PASSKEY: str = Field(default="")
    MPESA_INITIATOR_NAME: str = Field(default="testapi")
    MPESA_INITIATOR_PASSWORD: str = Field(default="")
    
    # B2C Configuration
    MPESA_B2C_QUEUE_TIMEOUT_URL: str = Field(default="https://yourdomain.com/api/v1/mpesa/b2c/timeout")
    MPESA_B2C_RESULT_URL: str = Field(default="https://yourdomain.com/api/v1/mpesa/b2c/result")
    MPESA_COMMAND_ID: str = Field(default="BusinessPayment")
    
    # Safety settings
    ENABLE_REAL_PAYMENTS: bool = Field(default=False, description="MUST be false until production ready")
    PAYMENT_DRY_RUN_DEFAULT: bool = Field(default=True)
    PAYMENT_MAX_AMOUNT_DAILY: Decimal = Field(default=Decimal("1000000"))
    PAYMENT_MIN_AMOUNT: Decimal = Field(default=Decimal("100"))
    REQUIRE_PAYMENT_APPROVAL: bool = Field(default=False)
    
    # ============================================
    # BUSINESS LOGIC
    # ============================================
    PRICE_PER_LITER: Decimal = Field(default=Decimal("45.00"))
    QUALITY_GRADE_A_MULTIPLIER: Decimal = Field(default=Decimal("1.10"))
    QUALITY_GRADE_B_MULTIPLIER: Decimal = Field(default=Decimal("1.00"))
    QUALITY_GRADE_C_MULTIPLIER: Decimal = Field(default=Decimal("0.85"))
    MINIMUM_PAYMENT_THRESHOLD: Decimal = Field(default=Decimal("100.00"))
    
    # Delivery validation
    MIN_DELIVERY_LITERS: Decimal = Field(default=Decimal("0.1"))
    MAX_DELIVERY_LITERS: Decimal = Field(default=Decimal("200.0"))
    
    # Quality grading
    GRADE_A_MIN_FAT_CONTENT: Decimal = Field(default=Decimal("3.5"))
    GRADE_B_MIN_FAT_CONTENT: Decimal = Field(default=Decimal("3.0"))
    GRADE_C_MIN_FAT_CONTENT: Decimal = Field(default=Decimal("2.5"))
    
    # ============================================
    # MONITORING & OBSERVABILITY
    # ============================================
    SENTRY_DSN: Optional[str] = Field(default=None)
    SENTRY_ENVIRONMENT: str = Field(default="development")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1)
    
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PORT: int = Field(default=9090)
    
    LOG_JSON_FORMAT: bool = Field(default=False)
    LOG_PII_MASKING: bool = Field(default=True)
    
    # ============================================
    # STORAGE & BACKUP
    # ============================================
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    S3_BUCKET_BACKUPS: str = Field(default="ddcpts-backups")
    S3_BUCKET_ARCHIVES: str = Field(default="ddcpts-archives")
    
    BACKUP_RETENTION_DAYS: int = Field(default=30)
    ARCHIVE_AFTER_MONTHS: int = Field(default=12)
    
    # ============================================
    # REDIS (for background tasks and caching)
    # ============================================
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=50)
    
    # ============================================
    # LOCALIZATION
    # ============================================
    DEFAULT_LANGUAGE: str = Field(default="en")
    SUPPORTED_LANGUAGES: str = Field(default="en,sw")
    DEFAULT_TIMEZONE: str = Field(default="Africa/Nairobi")
    DEFAULT_CURRENCY: str = Field(default="KES")
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Parse supported languages from comma-separated string."""
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]
    
    # ============================================
    # FEATURE FLAGS
    # ============================================
    ENABLE_2FA: bool = Field(default=False)
    ENABLE_FARMER_FEEDBACK: bool = Field(default=True)
    ENABLE_BULK_IMPORT: bool = Field(default=True)
    ENABLE_ANALYTICS_DASHBOARD: bool = Field(default=True)
    ENABLE_OFFLINE_SYNC: bool = Field(default=True)
    
    # ============================================
    # DEVELOPMENT & TESTING
    # ============================================
    TEST_DATABASE_URL: Optional[PostgresDsn] = Field(default=None)
    USE_MOCK_SMS: bool = Field(default=False)
    USE_MOCK_PAYMENTS: bool = Field(default=False)
    CREATE_SEED_DATA: bool = Field(default=False)
    SEED_ADMIN_EMAIL: str = Field(default="admin@ddcpts.test")
    SEED_ADMIN_PASSWORD: str = Field(default="Admin@123")
    
    # ============================================
    # PRODUCTION ONLY
    # ============================================
    FORCE_HTTPS: bool = Field(default=False)
    HSTS_MAX_AGE: int = Field(default=31536000)
    USE_AWS_SECRETS_MANAGER: bool = Field(default=False)
    AWS_SECRETS_MANAGER_SECRET_NAME: Optional[str] = Field(default=None)
    
    # ============================================
    # MOBILE APP CONFIGURATION
    # ============================================
    MOBILE_API_BASE_URL: str = Field(default="http://localhost:8000/api/v1")
    SYNC_INTERVAL_MINUTES: int = Field(default=30)
    SYNC_BATCH_SIZE: int = Field(default=100)
    SYNC_RETRY_ATTEMPTS: int = Field(default=5)
    OFFLINE_MAX_DELIVERIES: int = Field(default=1000)
    OFFLINE_DATA_RETENTION_DAYS: int = Field(default=90)
    
    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars
    )
    
    def get_quality_multiplier(self, grade: str) -> Decimal:
        """Get payment multiplier for a quality grade."""
        multipliers = {
            "A": self.QUALITY_GRADE_A_MULTIPLIER,
            "B": self.QUALITY_GRADE_B_MULTIPLIER,
            "C": self.QUALITY_GRADE_C_MULTIPLIER,
            "Rejected": Decimal("0.00"),
        }
        return multipliers.get(grade, Decimal("1.00"))
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
settings = Settings()


# Helper function to get settings (useful for dependency injection)
def get_settings() -> Settings:
    """
    Get application settings.
    
    This function can be used as a FastAPI dependency to inject settings
    into route handlers.
    """
    return settings
