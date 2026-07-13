import json
from typing import Any, Dict, List, Union
from pydantic import AnyHttpUrl, field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings configuration class loader.
    Leverages pydantic-settings to automatically parse and validate 
    environment variables defined in the .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Project Metadata
    PROJECT_NAME: str = "Qyverion"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # FastAPI Web Server Config
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Parses JSON strings of CORS origins into a list of strings.
        Useful when parsing serialized values from .env.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return v

    # PostgreSQL Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "qyverion"

    # Configurable database connection URL
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, info: Any) -> str:
        """
        Dynamically constructs the database URL if not explicitly provided in env.
        """
        if v:
            return v
        
        # Access field values from info.data if available
        # Fall back to defaults if not set in environment or in process of initialization
        data = info.data
        user = data.get("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD", "changeme")
        server = data.get("POSTGRES_SERVER", "localhost")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "qyverion")
        
        return f"postgresql://{user}:{password}@{server}:{port}/{db}"

    # Security Configuration
    SECRET_KEY: str = "replace_this_with_a_secure_random_hex_key_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


# Instantiate settings singleton
settings = Settings()
