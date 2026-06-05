from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    mongodb_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    remember_me_token_expire_days: int = 30

    # Server
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Facebook
    facebook_page_token_1: str = ""
    facebook_page_token_2: str = ""
    facebook_cache_refresh_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
