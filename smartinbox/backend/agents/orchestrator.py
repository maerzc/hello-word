"""
Orchestrator Agent - Klassifiziert E-Mails und routet sie an spezialisierte Agenten
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator Agent für E-Mail-Klassifikation
    Analysiert eingehende E-Mails und klassifiziert sie in:
    - quote_request (Angebotsanfrage)
    - invoice (Rechnung)
    - support (Support-Anfrage)
    - newsletter (Newsletter)
    - appointment (Beratungstermin)
    """

    def __init__(self, prompts: dict):
        """
        Initialisiert den Orchestrator

        Args:
            prompts: Dictionary mit Prompt-Templates
        """
        self.system_prompt = prompts.get("orchestrator", self._default_prompt())
        logger.info("Orchestrator Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein intelligenter E-Mail-Klassifikations-Agent.

Deine Aufgabe ist es, eingehende E-Mails zu analysieren und in eine der folgenden Kategorien einzuordnen:

1. **quote_request** - Angebotsanfragen
   Kennzeichen: Anfragen nach Preisen, Produkten, Dienstleistungen, RFPs

2. **invoice** - Rechnungen
   Kennzeichen: Rechnungsnummern, Zahlungsaufforderungen, Beträge

3. **support** - Support-Anfragen
   Kennzeichen: Probleme, Fehler, technische Fragen, Hilferufe

4. **newsletter** - Newsletter
   Kennzeichen: Marketing, Rundschreiben, Updates, Abmelde-Links

5. **appointment** - Terminanfragen
   Kennzeichen: Termin, Meeting, Beratung, Zeitvorschläge

Antworte IMMER im folgenden JSON-Format:
{
    "classification": "kategorie",
    "confidence": 0.95,
    "reasoning": "Kurze Begründung"
}"""

    def classify(self, state: SmartInboxState) -> SmartInboxState:
        """
        Klassifiziert die E-Mail im State

        Args:
            state: Aktueller State mit E-Mail-Daten

        Returns:
            Aktualisierter State mit Klassifikation
        """
        try:
            # Log-Eintrag hinzufügen
            state["agent_steps"].append(AgentStep(
                agent_name="Orchestrator",
                action="classify_email",
                timestamp=datetime.now().isoformat(),
                details=f"Klassifiziere E-Mail von {state['email']['sender']}",
                status="started"
            ))

            email = state["email"]
            email_text = f"""
Absender: {email['sender']}
Betreff: {email['subject']}
Inhalt:
{email['body']}
"""

            # LLM-Aufruf zur Klassifikation
            response = llm_client.invoke(
                system_prompt=self.system_prompt,
                user_message=email_text
            )

            # Parse JSON-Response
            try:
                result = json.loads(response)
                classification = result.get("classification", "support")
                confidence = result.get("confidence", 0.5)
                reasoning = result.get("reasoning", "Keine Begründung")

                logger.info(f"E-Mail klassifiziert als: {classification} (Confidence: {confidence})")

            except json.JSONDecodeError:
                # Fallback: Versuche Klassifikation aus Text zu extrahieren
                logger.warning("JSON-Parsing fehlgeschlagen, verwende Fallback")
                classification = self._extract_classification_fallback(response)
                confidence = 0.5
                reasoning = "Fallback-Klassifikation"

            # State aktualisieren
            state["classification"] = classification
            state["classification_confidence"] = confidence

            # Erfolgsmeldung
            state["agent_steps"].append(AgentStep(
                agent_name="Orchestrator",
                action="classify_email",
                timestamp=datetime.now().isoformat(),
                details=f"Klassifiziert als: {classification} ({reasoning})",
                status="completed"
            ))

            return state

        except Exception as e:
            logger.error(f"Fehler bei E-Mail-Klassifikation: {str(e)}")
            state["error"] = f"Klassifikationsfehler: {str(e)}"
            state["workflow_status"] = "failed"

            state["agent_steps"].append(AgentStep(
                agent_name="Orchestrator",
                action="classify_email",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))

            return state

    def _extract_classification_fallback(self, text: str) -> str:
        """Fallback-Methode zur Extraktion der Klassifikation aus dem Text"""
        text_lower = text.lower()

        if "quote_request" in text_lower or "angebot" in text_lower:
            return "quote_request"
        elif "invoice" in text_lower or "rechnung" in text_lower:
            return "invoice"
        elif "support" in text_lower or "hilfe" in text_lower:
            return "support"
        elif "newsletter" in text_lower:
            return "newsletter"
        elif "appointment" in text_lower or "termin" in text_lower:
            return "appointment"
        else:
            return "support"  # Default-Fallback
