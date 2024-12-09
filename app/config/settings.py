from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    MONGO_URI: str
    DATABASE_NAME: str
    RAPIDAPI_HOST:str
    RAPIDAPI_KEY:str
    ALGORITHM: str = "HS256"  

    class Config:
        env_file = ".env"

settings = Settings()
