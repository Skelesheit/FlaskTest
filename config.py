import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    provider = os.getenv("PROVIDER", "postgresql")
    driver = os.getenv("DRIVER", "psycopg2")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "mydb")

    secret_key = os.getenv("SECRET_KEY", "")
    expire_access_token_time = os.getenv("EXPIRES_ACCESS_TOKEN_MINUTES", 5)
    expire_refresh_token_time = os.getenv("EXPIRES_REFRESH_TOKEN_DAYS", 10)

    backend_host = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port = int(os.getenv("BACKEND_PORT", 8080))
    backend_debug = os.getenv("BACKEND_DEBUG", True)

    @property
    def db_url(self):
        return (
            f"{self.provider}+{self.driver}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
