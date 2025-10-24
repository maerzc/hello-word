"""
Terminagent - Bearbeitet Terminanfragen und schlägt Zeiten vor
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class AppointmentAgent:
    """
    Spezialisierter Agent für Terminanfragen
    Analysiert Terminwünsche und schlägt passende Zeiten vor
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Terminagenten"""
        self.system_prompt = prompts.get("appointment", self._default_prompt())
        logger.info("Appointment Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein spezialisierter Agent für Terminvereinbarungen.

Deine Aufgaben:
1. Analysiere die Terminanfrage und identifiziere:
   - Gewünschtes Datum/Zeitraum
   - Dauer des Termins
   - Thema/Zweck des Termins
   - Teilnehmer

2. Prüfe auf fehlende Informationen
3. Schlage konkrete Termine vor (wenn genug Infos vorhanden)

Antworte im JSON-Format:
{
    "topic": "Thema des Termins",
    "duration_minutes": 60,
    "preferred_dates": ["2025-01-20", "2025-01-21"],
    "missing_info": ["Bevorzugte Uhrzeit"],
    "suggested_slots": [
        {"date": "2025-01-20", "time": "10:00", "available": true},
        {"date": "2025-01-20", "time": "14:00", "available": true}
    ],
    "summary": "Zusammenfassung der Terminanfrage"
}"""

    def _generate_time_slots(self, days_ahead: int = 7) -> list:
        """Generiert verfügbare Zeitslots für die nächsten Tage"""
        slots = []
        today = datetime.now()

        for day_offset in range(1, days_ahead + 1):
            target_date = today + timedelta(days=day_offset)

            # Nur Werktage
            if target_date.weekday() < 5:  # Mo-Fr
                # Vormittags-Slots
                for hour in [9, 10, 11]:
                    slots.append({
                        "date": target_date.strftime("%Y-%m-%d"),
                        "time": f"{hour:02d}:00",
                        "available": True
                    })

                # Nachmittags-Slots
                for hour in [14, 15, 16]:
                    slots.append({
                        "date": target_date.strftime("%Y-%m-%d"),
                        "time": f"{hour:02d}:00",
                        "available": True
                    })

        return slots

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Verarbeitet die Terminanfrage

        Args:
            state: Aktueller Workflow-State

        Returns:
            Aktualisierter State mit Terminvorschlägen
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="AppointmentAgent",
                action="process_appointment_request",
                timestamp=datetime.now().isoformat(),
                details="Analysiere Terminanfrage",
                status="started"
            ))

            email = state["email"]
            email_text = f"""
Absender: {email['sender']}
Betreff: {email['subject']}
Inhalt:
{email['body']}

Verfügbare Zeitslots (nächste 7 Tage):
{json.dumps(self._generate_time_slots(), indent=2, ensure_ascii=False)}
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
                    "topic": "Beratungstermin",
                    "duration_minutes": 60,
                    "preferred_dates": [],
                    "missing_info": ["Bevorzugtes Datum", "Bevorzugte Uhrzeit"],
                    "suggested_slots": self._generate_time_slots()[:5],  # Erste 5 Slots
                    "summary": response
                }

            # State aktualisieren
            state["agent_results"]["appointment"] = result

            # Fehlende Infos markieren
            if result.get("missing_info"):
                state["missing_info"] = result["missing_info"]
                state["workflow_status"] = "waiting_for_user"

            # Erfolgsmeldung
            slot_count = len(result.get("suggested_slots", []))
            state["agent_steps"].append(AgentStep(
                agent_name="AppointmentAgent",
                action="process_appointment_request",
                timestamp=datetime.now().isoformat(),
                details=f"{slot_count} Terminvorschläge generiert",
                status="completed"
            ))

            logger.info("Terminanfrage erfolgreich verarbeitet")
            return state

        except Exception as e:
            logger.error(f"Fehler im AppointmentAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="AppointmentAgent",
                action="process_appointment_request",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state
