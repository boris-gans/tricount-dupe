# basic settings; db url, env vars
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_user: str = Field(default="mycountadmin", env="database-user")
    database_pw: str = Field(default="Hard-password", env="database-pw")
    database_name: str = Field(default="mycount", env="database-name")
    database_url_raw: str | None = Field(default=None, env="database-url")
    database_url_local: str | None = Field(default=None, env="database-url-local")

    jwt_secret_key: str = Field(default="testsecret", env="jwt-secret-key")
    jwt_algorithm: str = Field(default="HS256", env="jwt-algorithm")
    jwt_expiration_minutes: int = Field(default=15, env="jwt-expiration-minutes")

    log_format: str = Field(default="%(asctime)s | %(levelname)s | %(name)s | %(message)s", env="log-format")
    base_logger_name: str = Field(default="test", env="base-logger-name")
    frontend_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="frontend-origins"
    )

    @property
    def database_url(self) -> str:
        if not self.database_url_local and self.database_url_raw:
            normalized = self.database_url_raw

            # Convert postgres:// → postgresql+psycopg2://
            if normalized.startswith("postgres://"):
                normalized = "postgresql+psycopg2://" + normalized[len("postgres://"):]
            elif normalized.startswith("postgresql://"):
                normalized = "postgresql+psycopg2://" + normalized[len("postgresql://"):]

            # Make sure sslmode is required for Azure
            if "sslmode=" not in normalized:
                normalized += "?sslmode=require"

            return normalized

        # fallback
        return (
            f"postgresql+psycopg2://{self.database_user}:"
            f"{self.database_pw}@mycount-database.postgres.database.azure.com:"
            f"5432/{self.database_name}?sslmode=require"
        ) if not self.database_url_local else self.database_url_local
    class Config: #tell pydantic to load variables from .env (not in prod)
        env_file = ".env"

settings = Settings()
