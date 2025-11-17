"""
Base configuration for CIMR AI Agents
"""
import os
from dotenv import load_dotenv
from agno.models.azure import AzureOpenAI
from src.config import settings

load_dotenv()


def get_azure_model():
    """Get Azure OpenAI model configuration"""
    return AzureOpenAI(
        id=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    )
