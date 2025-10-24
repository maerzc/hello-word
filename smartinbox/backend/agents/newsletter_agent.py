"""
Newsletter-Agent - Extrahiert Schlagzeilen und erstellt Zusammenfassungen
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class NewsletterAgent:
    """
    Spezialisierter Agent für Newsletter
    Extrahiert wichtige Schlagzeilen und erstellt eine Kurzzusammenfassung
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Newsletter-Agenten"""
        self.system_prompt = prompts.get("newsletter", self._default_prompt())
        logger.info("Newsletter Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein spezialisierter Agent für Newsletter-Analyse.

Deine Aufgaben:
1. Extrahiere die wichtigsten Schlagzeilen aus dem Newsletter
2. Erstelle eine kompakte Zusammenfassung (max. 3-4 Sätze)
3. Identifiziere Kategorien (z.B. Produktnews, Events, Angebote)
4. Markiere zeitkritische Informationen (z.B. Angebote mit Ablaufdatum)

Antworte im JSON-Format:
{
    "headlines": ["Schlagzeile 1", "Schlagzeile 2", "Schlagzeile 3"],
    "summary": "Kurze Zusammenfassung des Newsletters",
    "categories": ["Produktnews", "Events"],
    "time_sensitive": ["Angebot läuft bis 31.12."],
    "sender": "Newsletter-Absender"
}"""

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Verarbeitet den Newsletter

        Args:
            state: Aktueller Workflow-State

        Returns:
            Aktualisierter State mit Newsletter-Zusammenfassung
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="NewsletterAgent",
                action="extract_headlines",
                timestamp=datetime.now().isoformat(),
                details="Extrahiere Schlagzeilen aus Newsletter",
                status="started"
            ))

            email = state["email"]
            email_text = f"""
Absender: {email['sender']}
Betreff: {email['subject']}
Inhalt:
{email['body']}
"""

            # LLM-Aufruf
            response = llm_client.invoke(
                system_prompt=self.system_prompt,
                user_message=email_text
            )

            # Parse Response
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                logger.warning("JSON-Parsing fehlgeschlagen, verwende Fallback")
                result = {
                    "headlines": ["Zusammenfassung nicht verfügbar"],
                    "summary": response[:200],  # Erste 200 Zeichen
                    "categories": ["Allgemein"],
                    "time_sensitive": [],
                    "sender": email['sender']
                }

            # State aktualisieren
            state["agent_results"]["newsletter"] = result

            # Erfolgsmeldung
            headline_count = len(result.get("headlines", []))
            state["agent_steps"].append(AgentStep(
                agent_name="NewsletterAgent",
                action="extract_headlines",
                timestamp=datetime.now().isoformat(),
                details=f"{headline_count} Schlagzeilen extrahiert",
                status="completed"
            ))

            logger.info("Newsletter erfolgreich verarbeitet")
            return state

        except Exception as e:
            logger.error(f"Fehler im NewsletterAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="NewsletterAgent",
                action="extract_headlines",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state
