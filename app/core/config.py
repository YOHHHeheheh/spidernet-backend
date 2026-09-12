from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SpiderNet Core"
    VERSION: str = "1.0.0-PROD"
    API_V1_STR: str = "/api/v1"
    
    NEO4J_URI: str = "neo4j+ssc://539338b1.databases.neo4j.io"
    NEO4J_USER: str = "539338b1"
    NEO4J_PASSWORD: str = "kDKkfrMs13UQQT1-B9uv_L_CrswIU6IobBzpSqnw3Eo"
    
    JWT_SECRET: str = "super_secure_le_s_secret_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
