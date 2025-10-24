"""
Angebotsagent - Bearbeitet Angebotsanfragen
Holt ggf. Daten aus einem simulierten CRM
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class QuoteAgent:
    """
    Spezialisierter Agent für Angebotsanfragen
    Analysiert die Anfrage und bereitet Angebotsinformationen vor
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Angebotsagenten"""
        self.system_prompt = prompts.get("quote", self._default_prompt())
        self.crm_data = self._load_mock_crm_data()
        logger.info("Quote Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein spezialisierter Agent für Angebotsanfragen.

Deine Aufgaben:
1. Analysiere die Angebotsanfrage und identifiziere:
   - Gewünschte Produkte/Dienstleistungen
   - Mengen und Spezifikationen
   - Budget oder Preisvorstellungen
   - Zeitrahmen

2. Prüfe, ob alle relevanten Informationen vorhanden sind
3. Erstelle eine strukturierte Zusammenfassung
4. Schlage passende Produkte aus dem CRM vor

Antworte im JSON-Format:
{
    "requested_products": ["Produkt 1", "Produkt 2"],
    "missing_info": ["fehlende Info 1"],
    "recommendations": ["Empfehlung 1"],
    "summary": "Zusammenfassung der Anfrage"
}"""

    def _load_mock_crm_data(self) -> dict:
        """Lädt Mock-CRM-Daten für Demo-Zwecke"""
        return {
            "products": [
                {"id": "P001", "name": "Cloud-Hosting Paket S", "price": 49.99, "category": "hosting"},
                {"id": "P002", "name": "Cloud-Hosting Paket M", "price": 99.99, "category": "hosting"},
                {"id": "P003", "name": "Cloud-Hosting Paket L", "price": 199.99, "category": "hosting"},
                {"id": "P004", "name": "Beratungspaket 5h", "price": 500.00, "category": "consulting"},
                {"id": "P005", "name": "Beratungspaket 10h", "price": 950.00, "category": "consulting"},
                {"id": "P006", "name": "Custom Software Entwicklung", "price": 5000.00, "category": "development"},
            ]
        }

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Verarbeitet die Angebotsanfrage

        Args:
            state: Aktueller Workflow-State

        Returns:
            Aktualisierter State mit Angebotsinformationen
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="QuoteAgent",
                action="process_quote_request",
                timestamp=datetime.now().isoformat(),
                details="Analysiere Angebotsanfrage",
                status="started"
            ))

            email = state["email"]
            email_text = f"""
Absender: {email['sender']}
Betreff: {email['subject']}
Inhalt:
{email['body']}

Verfügbare Produkte im CRM:
{json.dumps(self.crm_data, indent=2, ensure_ascii=False)}
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
                logger.warning("JSON-Parsing fehlgeschlagen, verwende Text-Response")
                result = {
                    "summary": response,
                    "requested_products": [],
                    "missing_info": [],
                    "recommendations": []
                }

            # State aktualisieren
            state["agent_results"]["quote"] = result

            # Fehlende Infos markieren
            if result.get("missing_info"):
                state["missing_info"] = result["missing_info"]
                state["workflow_status"] = "waiting_for_user"

            # Erfolgsmeldung
            state["agent_steps"].append(AgentStep(
                agent_name="QuoteAgent",
                action="process_quote_request",
                timestamp=datetime.now().isoformat(),
                details=f"Analyse abgeschlossen. {len(result.get('recommendations', []))} Empfehlungen",
                status="completed"
            ))

            logger.info("Angebotsanfrage erfolgreich verarbeitet")
            return state

        except Exception as e:
            logger.error(f"Fehler im QuoteAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="QuoteAgent",
                action="process_quote_request",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state
