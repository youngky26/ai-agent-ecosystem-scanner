from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str = ""
    database_url: str = "sqlite:///./scanner.db"
    scan_api_key: str = ""
    scan_limit: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
