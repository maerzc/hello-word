"""
LangGraph Workflow für das SmartInbox Agentensystem
Definiert die State Machine und orchestriert die Agenten
"""

from langgraph.graph import StateGraph, END
from .state import SmartInboxState
from .orchestrator import OrchestratorAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SmartInboxWorkflow:
    """
    Hauptworkflow für das SmartInbox-System
    Orchestriert die Agenten basierend auf E-Mail-Klassifikation
    """

    def __init__(self, prompts: Dict[str, str], agents: Dict[str, Any]):
        """
        Initialisiert den Workflow

        Args:
            prompts: Dictionary mit Prompt-Templates für alle Agenten
            agents: Dictionary mit initialisierten Agent-Instanzen
        """
        self.prompts = prompts
        self.agents = agents
        self.orchestrator = OrchestratorAgent(prompts)

        # Graph erstellen
        self.graph = self._build_graph()
        logger.info("SmartInbox Workflow initialisiert")

    def _build_graph(self) -> StateGraph:
        """
        Erstellt den LangGraph State Graph

        Returns:
            Kompilierter StateGraph
        """
        # Graph mit State-Schema initialisieren
        workflow = StateGraph(SmartInboxState)

        # Nodes hinzufügen
        workflow.add_node("orchestrator", self.orchestrator.classify)
        workflow.add_node("quote_agent", self._route_to_quote_agent)
        workflow.add_node("invoice_agent", self._route_to_invoice_agent)
        workflow.add_node("support_agent", self._route_to_support_agent)
        workflow.add_node("newsletter_agent", self._route_to_newsletter_agent)
        workflow.add_node("appointment_agent", self._route_to_appointment_agent)
        workflow.add_node("chat_agent", self._route_to_chat_agent)

        # Entry Point
        workflow.set_entry_point("orchestrator")

        # Conditional Edges vom Orchestrator
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_based_on_classification,
            {
                "quote_request": "quote_agent",
                "invoice": "invoice_agent",
                "support": "support_agent",
                "newsletter": "newsletter_agent",
                "appointment": "appointment_agent",
                "error": END
            }
        )

        # Alle Spezialagenten führen zum Chat-Agenten
        workflow.add_edge("quote_agent", "chat_agent")
        workflow.add_edge("invoice_agent", "chat_agent")
        workflow.add_edge("support_agent", "chat_agent")
        workflow.add_edge("newsletter_agent", "chat_agent")
        workflow.add_edge("appointment_agent", "chat_agent")

        # Chat-Agent beendet den Workflow
        workflow.add_edge("chat_agent", END)

        # Graph kompilieren
        return workflow.compile()

    def _route_based_on_classification(self, state: SmartInboxState) -> str:
        """
        Routing-Funktion basierend auf E-Mail-Klassifikation

        Args:
            state: Aktueller State mit Klassifikation

        Returns:
            Name des nächsten Agenten
        """
        if state.get("error"):
            return "error"

        classification = state.get("classification", "support")
        logger.info(f"Route zu Agent: {classification}")
        return classification

    def _route_to_quote_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zur Angebotsagenten"""
        if "quote" in self.agents:
            return self.agents["quote"].process(state)
        return state

    def _route_to_invoice_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zum Rechnungsagenten"""
        if "invoice" in self.agents:
            return self.agents["invoice"].process(state)
        return state

    def _route_to_support_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zum Support-Agenten"""
        if "support" in self.agents:
            return self.agents["support"].process(state)
        return state

    def _route_to_newsletter_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zum Newsletter-Agenten"""
        if "newsletter" in self.agents:
            return self.agents["newsletter"].process(state)
        return state

    def _route_to_appointment_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zum Termin-Agenten"""
        if "appointment" in self.agents:
            return self.agents["appointment"].process(state)
        return state

    def _route_to_chat_agent(self, state: SmartInboxState) -> SmartInboxState:
        """Route zum Chat-Agenten (finale Nutzerinteraktion)"""
        if "chat" in self.agents:
            return self.agents["chat"].process(state)
        return state

    def run(self, state: SmartInboxState) -> SmartInboxState:
        """
        Führt den Workflow aus

        Args:
            state: Initialer State mit E-Mail

        Returns:
            Finaler State nach Workflow-Durchlauf
        """
        try:
            logger.info("Starte Workflow-Ausführung")
            result = self.graph.invoke(state)
            logger.info("Workflow erfolgreich abgeschlossen")
            return result

        except Exception as e:
            logger.error(f"Fehler bei Workflow-Ausführung: {str(e)}")
            state["error"] = str(e)
            state["workflow_status"] = "failed"
            return state
