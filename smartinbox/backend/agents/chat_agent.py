"""
Chat-Agent - Generiert benutzerfreundliche Antworten basierend auf Agentenergebnissen
"""

from .state import SmartInboxState, AgentStep, Message
from utils.llm import llm_client
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    User-Chat-Agent für finale Interaktion
    Nimmt Ergebnisse aller Spezialagenten und generiert eine freundliche Antwort
    """

    def __init__(self, prompts: dict):
        """Initialisiert den Chat-Agenten"""
        self.system_prompt = prompts.get("chat", self._default_prompt())
        logger.info("Chat Agent initialisiert")

    def _default_prompt(self) -> str:
        """Fallback System-Prompt"""
        return """Du bist ein freundlicher virtueller Assistent für das SmartInbox-System.

Deine Aufgaben:
1. Nimm die Ergebnisse der Spezialagenten und formuliere eine menschliche, freundliche Antwort
2. Stelle fehlende Informationen als Fragen
3. Fasse komplexe Informationen verständlich zusammen
4. Sei proaktiv und hilfsbereit

Stil:
- Professionell aber nahbar
- Klar und präzise
- Bei Problemen: lösungsorientiert
- Bei fehlenden Infos: konkrete Rückfragen

Beispiele:
- "Vielen Dank für Ihre Anfrage! Ich habe Ihre E-Mail analysiert..."
- "Um Ihnen bestmöglich zu helfen, benötige ich noch folgende Informationen..."
- "Ich habe 3 passende Terminvorschläge für Sie gefunden..."
"""

    def process(self, state: SmartInboxState) -> SmartInboxState:
        """
        Generiert finale Chat-Antwort basierend auf allen Agentenergebnissen

        Args:
            state: Aktueller Workflow-State mit allen Agentenergebnissen

        Returns:
            Aktualisierter State mit finaler User-Antwort
        """
        try:
            # Log-Eintrag
            state["agent_steps"].append(AgentStep(
                agent_name="ChatAgent",
                action="generate_response",
                timestamp=datetime.now().isoformat(),
                details="Generiere Benutzerantwort",
                status="started"
            ))

            # Kontext aus allen Agentenergebnissen zusammenstellen
            context = self._build_context(state)

            # LLM-Aufruf
            response = llm_client.invoke(
                system_prompt=self.system_prompt,
                user_message=context
            )

            # State aktualisieren
            state["final_response"] = response

            # Nachricht zur Chat-Historie hinzufügen
            state["messages"].append(Message(
                role="assistant",
                content=response,
                timestamp=datetime.now().isoformat(),
                agent_name="ChatAgent"
            ))

            # Workflow-Status setzen
            if state.get("missing_info"):
                state["workflow_status"] = "waiting_for_user"
            else:
                state["workflow_status"] = "completed"

            # Erfolgsmeldung
            state["agent_steps"].append(AgentStep(
                agent_name="ChatAgent",
                action="generate_response",
                timestamp=datetime.now().isoformat(),
                details="Antwort generiert",
                status="completed"
            ))

            logger.info("Chat-Antwort erfolgreich generiert")
            return state

        except Exception as e:
            logger.error(f"Fehler im ChatAgent: {str(e)}")
            state["agent_steps"].append(AgentStep(
                agent_name="ChatAgent",
                action="generate_response",
                timestamp=datetime.now().isoformat(),
                details=f"Fehler: {str(e)}",
                status="failed"
            ))
            return state

    def _build_context(self, state: SmartInboxState) -> str:
        """
        Baut den Kontext für die Chat-Antwort aus allen Agentenergebnissen

        Args:
            state: Aktueller State

        Returns:
            Formatierter Kontext-String
        """
        context_parts = []

        # E-Mail-Informationen
        email = state.get("email", {})
        context_parts.append(f"Eingehende E-Mail von: {email.get('sender', 'Unbekannt')}")
        context_parts.append(f"Betreff: {email.get('subject', 'Kein Betreff')}")
        context_parts.append(f"Klassifizierung: {state.get('classification', 'Unbekannt')}")

        # Agentenergebnisse
        agent_results = state.get("agent_results", {})

        if "quote" in agent_results:
            context_parts.append("\n--- Angebotsagent Ergebnisse ---")
            context_parts.append(json.dumps(agent_results["quote"], indent=2, ensure_ascii=False))

        if "invoice" in agent_results:
            context_parts.append("\n--- Rechnungsagent Ergebnisse ---")
            context_parts.append(json.dumps(agent_results["invoice"], indent=2, ensure_ascii=False))

        if "support" in agent_results:
            context_parts.append("\n--- Support-Agent Ergebnisse ---")
            context_parts.append(json.dumps(agent_results["support"], indent=2, ensure_ascii=False))

        if "newsletter" in agent_results:
            context_parts.append("\n--- Newsletter-Agent Ergebnisse ---")
            context_parts.append(json.dumps(agent_results["newsletter"], indent=2, ensure_ascii=False))

        if "appointment" in agent_results:
            context_parts.append("\n--- Terminagent Ergebnisse ---")
            context_parts.append(json.dumps(agent_results["appointment"], indent=2, ensure_ascii=False))

        # Fehlende Informationen
        if state.get("missing_info"):
            context_parts.append("\n--- Fehlende Informationen ---")
            context_parts.append(", ".join(state["missing_info"]))

        context_parts.append("\n--- Aufgabe ---")
        context_parts.append("Formuliere eine freundliche, hilfreiche Antwort an den Benutzer basierend auf den obigen Informationen.")

        return "\n".join(context_parts)

    def handle_user_response(self, state: SmartInboxState, user_message: str) -> SmartInboxState:
        """
        Verarbeitet eine Benutzerantwort im Chat

        Args:
            state: Aktueller State
            user_message: Nachricht vom Benutzer

        Returns:
            Aktualisierter State
        """
        try:
            # User-Nachricht zur Historie hinzufügen
            state["messages"].append(Message(
                role="user",
                content=user_message,
                timestamp=datetime.now().isoformat(),
                agent_name=None
            ))

            # Kontext mit Chat-Historie
            context = self._build_chat_context(state)

            # LLM-Aufruf mit Historie
            response = llm_client.invoke(
                system_prompt=self.system_prompt,
                user_message=context
            )

            # Antwort zur Historie hinzufügen
            state["messages"].append(Message(
                role="assistant",
                content=response,
                timestamp=datetime.now().isoformat(),
                agent_name="ChatAgent"
            ))

            state["final_response"] = response
            logger.info("User-Antwort verarbeitet")

            return state

        except Exception as e:
            logger.error(f"Fehler bei User-Response-Verarbeitung: {str(e)}")
            return state

    def _build_chat_context(self, state: SmartInboxState) -> str:
        """Baut Kontext mit Chat-Historie"""
        context_parts = [
            "Bisheriger Gesprächsverlauf:",
            ""
        ]

        for msg in state.get("messages", []):
            role = msg["role"]
            content = msg["content"]
            context_parts.append(f"{role.upper()}: {content}")

        return "\n".join(context_parts)
