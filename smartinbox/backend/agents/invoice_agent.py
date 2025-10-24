"""
Rechnungsagent - Prüft Rechnungen auf Vollständigkeit
"""

from .state import SmartInboxState, AgentStep
from utils.llm import llm_client
from datetime import datetime
import logging
import json
import re

logger = logging.getLogger(__name__)


class InvoiceAgent:
    """
    Spezialisierter Agent für Rechnungsprüfung
    Analysiert Rechnungen auf Vollständigkeit und Korrektheit
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Rechnungsagenten"""
        self.system_prompt = prompts.get("invoice", self._default_prompt())
        logger.info("Invoice Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein spezialisierter Agent für Rechnungsprüfung.

Deine Aufgaben:
1. Prüfe die Rechnung auf folgende Pflichtangaben:
   - Rechnungsnummer
   - Rechnungsdatum
   - Absender (Name, Adresse)
   - Empfänger (Name, Adresse)
   - Leistungsbeschreibung
   - Einzelpreise und Gesamtbetrag
   - Zahlungsbedingungen
   - Steuernummer oder USt-IdNr.

2. Identifiziere fehlende Angaben
3. Prüfe auf Unstimmigkeiten (z.B. Summenfehler)
4. Erstelle eine Zusammenfassung

Antworte im JSON-Format:
{
    "invoice_number": "RE-12345",
    "invoice_date": "2025-01-15",
    "total_amount": 1234.56,
    "is_complete": true,
    "missing_fields": [],
    "issues": [],
    "summary": "Zusammenfassung"
}"""

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Verarbeitet die Rechnung

        Args:
            state: Aktueller Workflow-State

        Returns:
            Aktualisierter State mit Rechnungsprüfung
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="InvoiceAgent",
                action="validate_invoice",
                timestamp=datetime.now().isoformat(),
                details="Prüfe Rechnung auf Vollständigkeit",
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
                result = self._fallback_invoice_analysis(email['body'])

            # State aktualisieren
            state["agent_results"]["invoice"] = result

            # Wenn Felder fehlen, User fragen
            if result.get("missing_fields"):
                state["missing_info"] = result["missing_fields"]
                state["workflow_status"] = "waiting_for_user"

            # Erfolgsmeldung
            status_msg = "vollständig" if result.get("is_complete") else "unvollständig"
            state["agent_steps"].append(AgentStep(
                agent_name="InvoiceAgent",
                action="validate_invoice",
                timestamp=datetime.now().isoformat(),
                details=f"Rechnung geprüft: {status_msg}",
                status="completed"
            ))

            logger.info("Rechnung erfolgreich geprüft")
            return state

        except Exception as e:
            logger.error(f"Fehler im InvoiceAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="InvoiceAgent",
                action="validate_invoice",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state

    def _fallback_invoice_analysis(self, text: str) -> dict:
        """Einfache Fallback-Analyse wenn LLM nicht JSON liefert"""
        result = {
            "invoice_number": None,
            "invoice_date": None,
            "total_amount": None,
            "is_complete": False,
            "missing_fields": [],
            "issues": [],
            "summary": "Automatische Analyse"
        }

        # Versuche Rechnungsnummer zu finden
        invoice_pattern = r'(?:Rechnung(?:snummer)?|Invoice|RE)[\s\-:]*([A-Z0-9\-]+)'
        match = re.search(invoice_pattern, text, re.IGNORECASE)
        if match:
            result["invoice_number"] = match.group(1)
        else:
            result["missing_fields"].append("Rechnungsnummer")

        # Versuche Betrag zu finden
        amount_pattern = r'(?:Summe|Gesamt|Total|Betrag)[\s:]*€?\s*([0-9.,]+)'
        match = re.search(amount_pattern, text, re.IGNORECASE)
        if match:
            result["total_amount"] = match.group(1)
        else:
            result["missing_fields"].append("Rechnungsbetrag")

        result["is_complete"] = len(result["missing_fields"]) == 0

        return result
