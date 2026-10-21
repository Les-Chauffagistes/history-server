from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gather_stats: bool
    port: int
    stats_api_token: str
    stats_url: str

    model_config = {"env_file": ".env", "extra": "allow"}

    @model_validator(mode="after")
    def _require_pool_api_config(self) -> "Settings":
        # le crawler ne peut pas fonctionner sans URL ni clé : échouer au chargement des settings
        if self.gather_stats and not (self.stats_url.strip() and self.stats_api_token.strip()):
            raise ValueError("STATS_URL et STATS_API_TOKEN doivent être non vides quand GATHER_STATS est actif")
        return self


settings = Settings()
