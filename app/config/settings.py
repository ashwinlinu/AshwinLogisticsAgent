from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ashwin Logistics AI Support Agent"
    app_version: str = "1.0.0"
    environment: str = "development"

    azure_openai_endpoint: str
    azure_openai_deployment: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()