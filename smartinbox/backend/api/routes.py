"""
FastAPI Routes für das SmartInbox Backend
Definiert alle API-Endpunkte
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from agents import (
    Email,
    SmartInboxState,
    create_initial_state,
    QuoteAgent,
    InvoiceAgent,
    SupportAgent,
    NewsletterAgent,
    AppointmentAgent,
    ChatAgent,
    SmartInboxWorkflow
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Globale Variablen für Workflow und Agenten
workflow_instance: Optional[SmartInboxWorkflow] = None
current_state: Optional[SmartInboxState] = None


# Pydantic Models für Request/Response
class EmailRequest(BaseModel):
    sender: str
    subject: str
    body: str
    attachments: Optional[List[str]] = None


class ProcessEmailResponse(BaseModel):
    status: str
    classification: Optional[str]
    agent_steps: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
    final_response: Optional[str]
    missing_info: Optional[List[str]]
    error: Optional[str]


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    response: str
    timestamp: str


@router.post("/process-email", response_model=ProcessEmailResponse)
async def process_email(email_request: EmailRequest):
    """
    Verarbeitet eine eingehende E-Mail durch das Agentensystem

    Args:
        email_request: E-Mail-Daten

    Returns:
        Verarbeitungsergebnis mit Klassifikation und Agentenschritten
    """
    global current_state, workflow_instance

    try:
        logger.info(f"Verarbeite E-Mail von {email_request.sender}")

        # E-Mail-Objekt erstellen
        email = Email(
            id=f"email_{datetime.now().timestamp()}",
            sender=email_request.sender,
            subject=email_request.subject,
            body=email_request.body,
            received_at=datetime.now().isoformat(),
            attachments=email_request.attachments or []
        )

        # Initial State erstellen
        state = create_initial_state(email)

        # Workflow ausführen (wenn initialisiert)
        if workflow_instance:
            result = workflow_instance.run(state)
            current_state = result
        else:
            logger.warning("Workflow nicht initialisiert, verwende Mock-Response")
            result = state
            result["classification"] = "support"
            result["workflow_status"] = "completed"
            result["final_response"] = "Workflow nicht initialisiert. Bitte Prompts laden."

        # Response erstellen
        return ProcessEmailResponse(
            status=result.get("workflow_status", "unknown"),
            classification=result.get("classification"),
            agent_steps=result.get("agent_steps", []),
            messages=result.get("messages", []),
            final_response=result.get("final_response"),
            missing_info=result.get("missing_info"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Fehler bei E-Mail-Verarbeitung: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(chat_request: ChatMessageRequest):
    """
    Sendet eine Chat-Nachricht an den Chat-Agenten

    Args:
        chat_request: Chat-Nachricht

    Returns:
        Antwort vom Chat-Agenten
    """
    global current_state

    try:
        if not current_state:
            raise HTTPException(
                status_code=400,
                detail="Kein aktiver Workflow. Bitte zuerst eine E-Mail verarbeiten."
            )

        logger.info(f"Verarbeite Chat-Nachricht: {chat_request.message[:50]}...")

        # Chat-Agent verwenden
        chat_agent = ChatAgent({})
        updated_state = chat_agent.handle_user_response(
            current_state,
            chat_request.message
        )

        current_state = updated_state

        return ChatMessageResponse(
            response=updated_state.get("final_response", "Keine Antwort"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Chat-Nachricht: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health Check Endpoint

    Returns:
        Status des Backends
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "workflow_initialized": workflow_instance is not None
    }


@router.get("/state")
async def get_current_state():
    """
    Gibt den aktuellen Workflow-State zurück

    Returns:
        Aktueller State
    """
    if not current_state:
        raise HTTPException(status_code=404, detail="Kein aktiver State vorhanden")

    return {
        "classification": current_state.get("classification"),
        "workflow_status": current_state.get("workflow_status"),
        "agent_steps": current_state.get("agent_steps", []),
        "messages": current_state.get("messages", []),
        "missing_info": current_state.get("missing_info")
    }


@router.post("/reset")
async def reset_state():
    """
    Setzt den aktuellen State zurück

    Returns:
        Bestätigung
    """
    global current_state
    current_state = None

    logger.info("State zurückgesetzt")

    return {
        "status": "success",
        "message": "State wurde zurückgesetzt"
    }


def initialize_workflow(prompts: Dict[str, str]):
    """
    Initialisiert den Workflow mit Prompts

    Args:
        prompts: Dictionary mit Prompt-Templates
    """
    global workflow_instance

    logger.info("Initialisiere Workflow mit Prompts")

    # Agenten initialisieren
    agents = {
        "quote": QuoteAgent(prompts),
        "invoice": InvoiceAgent(prompts),
        "support": SupportAgent(prompts),
        "newsletter": NewsletterAgent(prompts),
        "appointment": AppointmentAgent(prompts),
        "chat": ChatAgent(prompts)
    }

    # Workflow erstellen
    workflow_instance = SmartInboxWorkflow(prompts, agents)

    logger.info("Workflow erfolgreich initialisiert")
