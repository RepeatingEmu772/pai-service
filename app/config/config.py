import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("APP_ENV", "local")
env_file_map = {
    "local": ".env.local",
    "stg": ".env.stg",
    "prod": ".env.prod"
}
env_file = env_file_map.get(env, ".env.local")

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    openai_api_key: str
    pg_connect_str: str
    app_env: str = "local"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=env_file)

@lru_cache
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()
