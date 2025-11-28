# basic settings; db url, env vars
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_user: str = Field(..., env="database-user")
    database_pw: str = Field(..., env="database-pw")
    database_name: str = Field(..., env="database-name")
    database_url_raw: str = Field(..., env="database-url")

    jwt_secret_key: str = Field(..., env="jwt-secret-key")
    jwt_algorithm: str = Field(..., env="jwt-algorithm")
    jwt_expiration_minutes: int = Field(..., env="jwt-expiration-minutes")

    log_format: str = Field(..., env="log-format")
    base_logger_name: str = Field(..., env="base-logger-name")
    frontend_origins: list[str] = Field(
        default=["http://localhost:3000"],
        env="frontend-origins"
    )


    def database_url(self) -> str:
        if self.database_url_raw:
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
            f"postgresql+psycopg2://{self.database_user}@mycount-database:"
            f"{self.database_pw}@mycount-database.postgres.database.azure.com:"
            f"5432/{self.database_name}?sslmode=require"
        )


    class Config: #tell pydantic to load variables from .env (not in prod)
        env_file = None

settings = Settings()
