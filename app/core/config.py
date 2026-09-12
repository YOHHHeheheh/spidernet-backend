from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SpiderNet Core"
    VERSION: str = "1.0.0-PROD"
    API_V1_STR: str = "/api/v1"
    
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
