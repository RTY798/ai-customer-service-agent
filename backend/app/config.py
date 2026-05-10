from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"
    host: str = "0.0.0.0"
    port: int = 8000
    chroma_persist_dir: str = "./chroma_db"
    data_provider: str = "demo"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
