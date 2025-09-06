from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str = "default-secret"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost/"
    USER_SERVICE_URL: str = "http://localhost:8001"
    PRODUCT_SERVICE_URL: str = "http://localhost:8002"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()