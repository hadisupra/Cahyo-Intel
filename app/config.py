"""Application configuration using pydantic-settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CAHYO Intelligence - Olist E-Commerce RAG System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "olist_products"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./olist_ecommerce.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
