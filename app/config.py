from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://tradewars:tradewars@localhost:5432/tradewars"
    JWT_SECRET: str = "change-me-in-production"
    TICK_API_KEY: str = "change-me-in-production"
    TURNS_PER_DAY: int = 300
    GALAXY_SIZE: int = 500

    model_config = {"env_prefix": "TW_"}


settings = Settings()
