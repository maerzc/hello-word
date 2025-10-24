"""
SmartInbox Backend Configuration
Lädt Umgebungsvariablen und stellt zentrale Konfiguration bereit
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Zentrale Konfiguration für das SmartInbox Backend"""

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2:13b"

    # Backend Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    log_level: str = "INFO"

    # Frontend URL (CORS)
    frontend_url: str = "http://localhost:5173"

    # Data Paths
    faq_path: str = "../data/faq/support_faq.json"
    mails_path: str = "../data/mails/"
    prompts_path: str = "../prompts/"

    # Agent Configuration
    max_iterations: int = 10
    agent_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton Instance
settings = Settings()
