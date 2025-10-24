"""
Support-Agent - Beantwortet Support-Anfragen mit Hilfe einer FAQ-Datei
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime
from config.settings import settings
import logging
import json
import os

logger = logging.getLogger(__name__)


class SupportAgent:
    """
    Spezialisierter Agent für Support-Anfragen
    Durchsucht FAQ-Datei und beantwortet Fragen
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Support-Agenten"""
        self.system_prompt = prompts.get("support", self._default_prompt())
        self.faq_data = self._load_faq()
        logger.info("Support Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein spezialisierter Support-Agent.

Deine Aufgaben:
1. Analysiere die Support-Anfrage des Kunden
2. Durchsuche die FAQ-Datenbank nach passenden Antworten
3. Wenn eine Lösung gefunden wurde, formuliere eine freundliche Antwort
4. Wenn keine Lösung gefunden wurde, eskaliere an menschlichen Support

Antworte im JSON-Format:
{
    "problem_category": "Login-Probleme",
    "solution_found": true,
    "faq_matches": ["FAQ-ID-1", "FAQ-ID-2"],
    "response": "Freundliche Antwort an den Kunden",
    "escalate": false
}"""

    def _load_faq(self) -> list:
        """Lädt die FAQ-Daten"""
        try:
            faq_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                settings.faq_path
            )

            if os.path.exists(faq_path):
                with open(faq_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"FAQ-Datei nicht gefunden: {faq_path}, verwende Mock-Daten")
                return self._get_mock_faq()

        except Exception as e:
            logger.error(f"Fehler beim Laden der FAQ: {str(e)}")
            return self._get_mock_faq()

    def _get_mock_faq(self) -> list:
        """Mock-FAQ für Demo-Zwecke"""
        return [
            {
                "id": "FAQ-001",
                "category": "Login",
                "question": "Ich kann mich nicht einloggen",
                "answer": "Bitte prüfen Sie: 1) Caps Lock ist aus, 2) Korrekter Benutzername, 3) Passwort zurücksetzen über 'Passwort vergessen'"
            },
            {
                "id": "FAQ-002",
                "category": "Rechnung",
                "question": "Wo finde ich meine Rechnungen?",
                "answer": "Ihre Rechnungen finden Sie im Kundenportal unter 'Mein Konto' -> 'Rechnungen'"
            },
            {
                "id": "FAQ-003",
                "category": "Technisch",
                "question": "Die Seite lädt nicht",
                "answer": "Bitte leeren Sie Ihren Browser-Cache (Strg+F5) oder verwenden Sie den Inkognito-Modus"
            },
            {
                "id": "FAQ-004",
                "category": "Konto",
                "question": "Wie ändere ich meine E-Mail-Adresse?",
                "answer": "Gehen Sie zu 'Einstellungen' -> 'Profil' und klicken Sie auf 'E-Mail ändern'"
            }
        ]

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Verarbeitet die Support-Anfrage

        Args:
            state: Aktueller Workflow-State

        Returns:
            Aktualisierter State mit Support-Antwort
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="SupportAgent",
                action="search_faq",
                timestamp=datetime.now().isoformat(),
                details="Durchsuche FAQ-Datenbank",
                status="started"
            ))

            email = state["email"]
            email_text = f"""
Absender: {email['sender']}
Betreff: {email['subject']}
Inhalt:
{email['body']}

Verfügbare FAQ-Einträge:
{json.dumps(self.faq_data, indent=2, ensure_ascii=False)}
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
                logger.warning("JSON-Parsing fehlgeschlagen")
                result = {
                    "problem_category": "Unbekannt",
                    "solution_found": False,
                    "faq_matches": [],
                    "response": response,
                    "escalate": True
                }

            # State aktualisieren
            state["agent_results"]["support"] = result

            # Bei Eskalation -> User informieren
            if result.get("escalate"):
                state["workflow_status"] = "waiting_for_user"
                state["missing_info"] = ["Bitte kontaktieren Sie unseren Support direkt"]

            # Erfolgsmeldung
            status = "Lösung gefunden" if result.get("solution_found") else "Eskalation erforderlich"
            state["agent_steps"].append(AgentStep(
                agent_name="SupportAgent",
                action="search_faq",
                timestamp=datetime.now().isoformat(),
                details=status,
                status="completed"
            ))

            logger.info("Support-Anfrage erfolgreich verarbeitet")
            return state

        except Exception as e:
            logger.error(f"Fehler im SupportAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="SupportAgent",
                action="search_faq",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state
