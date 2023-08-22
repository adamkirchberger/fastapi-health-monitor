from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings defines parameters that can be overridden and their defaults.
    """

    heath_check_delay_seconds: int = 10

    # Read settings from .env file if one exists
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = Settings()
