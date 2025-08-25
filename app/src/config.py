import logging
import os
from typing import Any, List, Union

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator, SecretStr
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
    port: int = Field(default=int(os.environ["PORT"]))
    environment: str = Field(default=os.environ["ENVIRONMENT"])
    log_level: str = Field(default=os.environ["LOG_LEVEL"])

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str):
        level = getattr(logging, value.upper(), None)
        if not isinstance(level, int):
            raise ValueError(f"Invalid log level: {value}")
        return level


class CORSConfig(BaseSettings):
    allow_origins: str
    allow_methods: str
    allow_headers: str
    allow_credentials: bool

    @property
    def get_allow_origins(self):
        return self._split_strings(self.allow_origins)
    
    @property
    def get_allow_methods(self):
        return self._split_strings(self.allow_methods)
    
    @property
    def get_allow_headers(self):
        return self._split_strings(self.allow_headers)
    
    @property
    def get_allow_credentials(self):
        if isinstance(self.allow_credentials, str):
            return self.allow_credentials.lower() == "true"
        return self.allow_credentials
    
    def _split_strings(self, strings: str) -> List[str]:
        return [item.strip() for item in strings.split(",")]


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


class TokenConfig(BaseSettings):
    access_token_cookie_key: str
    refresh_token_cookie_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int # короткий токен (15-30 мин.)
    refresh_token_expire_days: int # длинный токен (7-30 дней)


class ArgonConfig(BaseSettings):
    argon2_time_cost: int
    argon2_memory_cost: int
    argon2_parallelism: int


class Config(BaseModel):
    app: AppConfig
    cors: CORSConfig
    token: TokenConfig
    argon2: ArgonConfig
    postgres: PostgresConfig


def create_config() -> Config:
    return Config(
        app=AppConfig(),
        cors=CORSConfig(),
        token=TokenConfig(),
        argon2=ArgonConfig(),
        postgres=PostgresConfig(),
    )
