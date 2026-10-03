from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class AppSettings(BaseSettings):
    llama_cloud_api_key: str
    # openai_api_key: str
    # model_name: str
    # model_endpoint: str

    api_timeout:int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )


appSettings = AppSettings()
