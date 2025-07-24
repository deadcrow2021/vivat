import logging
import os

from pydantic import BaseModel, Field, field_validator, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL

from dotenv import load_dotenv

load_dotenv()


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


class AppConfig(BaseSettings):
    environment: str = Field(default=os.environ["ENVIRONMENT"])
    log_level: str = Field(default=os.environ["LOG_LEVEL"])

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str):
        level = getattr(logging, value.upper(), None)
        if not isinstance(level, int):
            raise ValueError(f"Invalid log level: {value}")
        return level


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str
    debug: bool

    def build_dsn(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(hide_password=False)


class Config(BaseModel):
    app: AppConfig
    postgres: PostgresConfig


def create_config() -> Config:
    return Config(
        app=AppConfig(),
        postgres=PostgresConfig(),
    )
