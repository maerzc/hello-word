"""
State-Definitionen für das SmartInbox Agentensystem
Definiert die Datenstruktur, die zwischen Agenten weitergereicht wird
"""

from typing import TypedDict, Annotated, List, Optional, Dict, Any
from datetime import datetime
import operator


class Message(TypedDict):
    """Einzelne Chat-Nachricht"""
    role: str  # "user", "assistant", "system", "agent"
    content: str
    timestamp: str
    agent_name: Optional[str]


class AgentStep(TypedDict):
    """Log-Eintrag eines Agentenschritts"""
    agent_name: str
    action: str
    timestamp: str
    details: Optional[str]
    status: str  # "started", "completed", "failed"


class Email(TypedDict):
    """Eingehende E-Mail Struktur"""
    id: str
    sender: str
    subject: str
    body: str
    received_at: str
    attachments: Optional[List[str]]


class SmartInboxState(TypedDict):
    """
    Zentraler State für das Agentensystem
    Wird durch alle Agenten weitergereicht und aktualisiert
    """
    # Eingehende E-Mail
    email: Optional[Email]

    # Klassifikation der E-Mail
    classification: Optional[str]  # "quote_request", "invoice", "support", "newsletter", "appointment"
    classification_confidence: Optional[float]

    # Chat-Historie
    messages: Annotated[List[Message], operator.add]

    # Agenten-Logs (für UI-Visualisierung)
    agent_steps: Annotated[List[AgentStep], operator.add]

    # Zwischenergebnisse einzelner Agenten
    agent_results: Dict[str, Any]

    # Fehlende Informationen, die vom User erfragt werden müssen
    missing_info: Optional[List[str]]

    # Status des Workflows
    workflow_status: str  # "processing", "waiting_for_user", "completed", "failed"

    # Finale Antwort
    final_response: Optional[str]

    # Fehlerinformationen
    error: Optional[str]


def create_initial_state(email: Email) -> SmartInboxState:
    """Erstellt den initialen State für eine neue E-Mail"""
    return SmartInboxState(
        email=email,
        classification=None,
        classification_confidence=None,
        messages=[],
        agent_steps=[],
        agent_results={},
        missing_info=None,
        workflow_status="processing",
        final_response=None,
        error=None
    )
