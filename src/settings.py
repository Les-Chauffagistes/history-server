from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gather_stats: bool
    port: int
    stats_api_token: str
    stats_url: str

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
