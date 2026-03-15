from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_PASSWORD: str

    # JWT
    JWT_ACCESS_TOKEN_SECRET_KEY: str
    JWT_REFRESH_TOKEN_SECRET_KEY: str

    # Session
    SESSION_SECRET_KEY: str = "change-me-in-production"

    # OpenAI
    OPENAI_API_KEY: str

    # Admin
    SUPER_ADMIN_LOGIN: str
    SUPER_ADMIN_PASSWORD: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # URLs for OAuth redirects
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    MOBILE_REDIRECT_SCHEME: str = "myapp"

    # RabbitMQ (optional)
    RABBITMQ_DEFAULT_USER: Optional[str] = None
    RABBITMQ_DEFAULT_PASS: Optional[str] = None
    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None

    @property
    def db_url(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        )

    @property
    def alembic_db_url(self) -> str:
        return "postgresql://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        )

    @property
    def rabbitmq_url(self) -> Optional[str]:
        if not all([self.RABBITMQ_DEFAULT_USER, self.RABBITMQ_DEFAULT_PASS,
                    self.RABBITMQ_HOST, self.RABBITMQ_PORT]):
            return None
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"
