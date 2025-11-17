"""
Configuration settings for CIMR Claims Automation v1
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "CIMR Claims Automation v1"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Airtable
    airtable_api_key: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = "claims"
    
    # Azure OpenAI
    azure_openai_deployment_name: str = "gpt-4o-mini"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    # Email Settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    sender_email: str = "noreply@cimr.ma"
    sender_name: str = "CIMR Service Réclamations"
    email_enabled: bool = False

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields


# Global settings instance
settings = Settings()
