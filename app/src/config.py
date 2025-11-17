import logging
import os
from typing import Any, List, Optional, Union

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
    domain: Optional[str] = Field(os.environ.get("DOMAIN"))
    static_files_base_url: str = Field(default="")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str):
        level = getattr(logging, value.upper(), None)
        if not isinstance(level, int):
            raise ValueError(f"Invalid log level: {value}")
        return level

    @property
    def resolved_static_files_base_url(self) -> str:
        """Динамически вычисляемый URL для статических файлов"""
        # Если явно задан в .env - используем его
        if self.static_files_base_url:
            return self.static_files_base_url.rstrip('/')
        
        # Иначе вычисляем автоматически с учетом /api префикса
        if self.environment == "production":
            domain = f'https://{self.domain}'
            # В production nginx обслуживает статику по /static (без /api)
            return f"{domain}/static"
        else:
            # В development FastAPI обслуживает статику по /api/static
            return f"http://localhost:{self.port}/api/static"


class BotConfig(BaseSettings):
    bot_api_key: str
    domain: Optional[str] = Field(os.environ.get("DOMAIN"))
    environment: str = Field(default=os.environ["ENVIRONMENT"])
    bot_host: str = Field(default=os.environ["BOT_HOST"])
    bot_port: int = Field(default=int(os.environ["BOT_PORT"]))

    @property
    def get_bot_app_url(self) -> str:
        """Динамически вычисляемый URL для сервиса с ботом"""        
        # Вычисляем автоматически с учетом /bot префикса
        if self.environment == "production":
            url = f'https://{self.domain}'
        else:
            # В development FastAPI обслуживает статику по /api/static
            url = f"http://{self.bot_host}:{self.bot_port}"

        return url


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
    bot: BotConfig
    cors: CORSConfig
    token: TokenConfig
    argon2: ArgonConfig
    postgres: PostgresConfig


def create_config() -> Config:
    return Config(
        app=AppConfig(),
        bot=BotConfig(),
        cors=CORSConfig(),
        token=TokenConfig(),
        argon2=ArgonConfig(),
        postgres=PostgresConfig(),
    )
