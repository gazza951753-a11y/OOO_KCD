from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://kcd_user:kcd_secret@localhost:5432/kcd_db"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FIRST_SUPERADMIN_EMAIL: str = "admin@kcd.ru"
    FIRST_SUPERADMIN_PASSWORD: str = "Admin123!"

    APP_ENV: str = "development"


settings = Settings()
