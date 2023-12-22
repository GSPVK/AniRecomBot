from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: SecretStr
    model_config = SettingsConfigDict(env_file='./.env', env_file_encoding='utf-8')


config = Settings()
