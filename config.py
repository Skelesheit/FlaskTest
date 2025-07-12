import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # База данных
    provider: str = os.getenv("PROVIDER", "postgresql")
    driver: str = os.getenv("DRIVER", "psycopg2")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "mydb")

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "")
    expire_access_token_time: int = int(os.getenv("EXPIRES_ACCESS_TOKEN_MINUTES", 20))
    expire_refresh_token_time: int = int(os.getenv("EXPIRES_REFRESH_TOKEN_DAYS", 10))

    # Flask backend
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", 8080))
    backend_debug: bool = os.getenv("BACKEND_DEBUG", "True").lower() in ("true", "1", "yes")

    # Email (SMTP)
    mail_secret: str = os.getenv("MAIL_SECRET", "")
    mail_server: str = os.getenv("MAIL_SERVER", "")
    mail_port: int = int(os.getenv("MAIL_PORT", 587))
    mail_use_tls: bool = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
    mail_username: str = os.getenv("MAIL_USERNAME", "")
    mail_password: str = os.getenv("MAIL_PASSWORD", "")
    mail_default_sender: str = os.getenv("MAIL_DEFAULT_SENDER", "")
    base_url: str = os.getenv("BASE_URL", "http://localhost:5000")

    # Vue Frontend
    frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5174")

    # Yandex captcha
    yandex_url_verify = os.getenv("YANDEX_URL_VERIFY")
    yandex_secret = os.getenv("YANDEX_CAPTCHA_SECRET")

    # Dadata service
    dadata_token = os.getenv("DADATA_TOKEN")
    dadata_api_url = os.getenv("DADATA_API_URL")

    @property
    def db_url(self) -> str:
        return (
            f"{self.provider}+{self.driver}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
