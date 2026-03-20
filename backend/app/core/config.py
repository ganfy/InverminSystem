from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.example",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "INVERMIN PAITITI - Sistema Comercial"
    app_env: str = "development"
    debug: bool = False

    # Base de datos
    # "postgresql" para desarrollo local Docker
    # "mssql" para producción Azure SQL Server
    db_engine: str = "postgresql"
    db_server: str
    db_port: int = 5432  # 5432 postgres | 1433 sqlserver
    db_name: str
    db_user: str
    db_password: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Azure Blob (vacío en desarrollo)
    azure_storage_connection_string: str = ""
    azure_storage_container_tickets: str = "tickets"
    azure_storage_container_certificados: str = "certificados"

    tesseract_path: str | None = None

    @property
    def database_url(self) -> str:
        if self.db_engine == "postgresql":
            return (
                f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
                f"@{self.db_server}:{self.db_port}/{self.db_name}"
            )
        elif self.db_engine == "mssql":
            driver = "ODBC+Driver+18+for+SQL+Server"
            return (
                f"mssql+pyodbc://{self.db_user}:{self.db_password}"
                f"@{self.db_server}:{self.db_port}/{self.db_name}"
                f"?driver={driver}&Encrypt=yes&TrustServerCertificate=yes"
            )
        else:
            raise ValueError(f"DB_ENGINE no soportado: {self.db_engine}")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
