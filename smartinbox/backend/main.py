"""
SmartInbox Backend - Haupteinstiegspunkt
FastAPI Server mit Agentensystem
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import json
from pathlib import Path

from config.settings import settings
from api import router, initialize_workflow

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI App erstellen
app = FastAPI(
    title="SmartInbox Agent System",
    description="KI-Agentensystem für intelligente E-Mail-Verarbeitung",
    version="1.0.0"
)

# CORS konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(router, prefix="/api", tags=["SmartInbox"])


@app.on_event("startup")
async def startup_event():
    """Wird beim Start des Servers ausgeführt"""
    logger.info("SmartInbox Backend startet...")

    # Prompts laden
    prompts = load_prompts()

    # Workflow initialisieren
    initialize_workflow(prompts)

    logger.info("Backend erfolgreich gestartet")
    logger.info(f"API verfügbar unter: http://{settings.backend_host}:{settings.backend_port}/api")
    logger.info(f"Dokumentation unter: http://{settings.backend_host}:{settings.backend_port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Wird beim Herunterfahren des Servers ausgeführt"""
    logger.info("SmartInbox Backend wird heruntergefahren...")


def load_prompts() -> dict:
    """
    Lädt alle Prompt-Templates aus dem prompts-Verzeichnis

    Returns:
        Dictionary mit Prompts für jeden Agenten
    """
    prompts = {}

    prompts_dir = Path(__file__).parent.parent / "prompts"

    if not prompts_dir.exists():
        logger.warning(f"Prompts-Verzeichnis nicht gefunden: {prompts_dir}")
        return {}

    # Alle .txt Dateien im prompts-Verzeichnis laden
    for prompt_file in prompts_dir.glob("*.txt"):
        agent_name = prompt_file.stem  # Dateiname ohne Endung
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts[agent_name] = f.read()
            logger.info(f"Prompt geladen: {agent_name}")
        except Exception as e:
            logger.error(f"Fehler beim Laden von {prompt_file}: {str(e)}")

    logger.info(f"{len(prompts)} Prompts erfolgreich geladen")

    return prompts


@app.get("/")
async def root():
    """Root Endpoint"""
    return {
        "name": "SmartInbox Agent System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
