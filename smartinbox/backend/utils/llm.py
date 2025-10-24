"""
LLM-Wrapper für Ollama-Integration
Stellt eine zentrale Schnittstelle für alle Agenten bereit
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config.settings import settings
from typing import List, Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)


class MockLLM:
    """Mock-LLM für Demo-Zwecke ohne Ollama"""

    def invoke(self, messages):
        """Generiert Mock-Antworten basierend auf dem Kontext"""
        user_msg = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_msg = msg.content
                break

        # Klassifikation erkennen
        if "klassifiziere" in user_msg.lower() or "absender:" in user_msg.lower():
            if "angebot" in user_msg.lower() or "hosting" in user_msg.lower():
                return type('obj', (object,), {'content': json.dumps({
                    "classification": "quote_request",
                    "confidence": 0.95,
                    "reasoning": "E-Mail enthält Angebotsanfrage für Cloud-Hosting"
                })})
            elif "rechnung" in user_msg.lower() or "re-" in user_msg.lower():
                return type('obj', (object,), {'content': json.dumps({
                    "classification": "invoice",
                    "confidence": 0.98,
                    "reasoning": "E-Mail enthält Rechnungsinformationen"
                })})
            elif "login" in user_msg.lower() or "problem" in user_msg.lower() or "hilfe" in user_msg.lower():
                return type('obj', (object,), {'content': json.dumps({
                    "classification": "support",
                    "confidence": 0.92,
                    "reasoning": "E-Mail ist eine Support-Anfrage"
                })})
            elif "newsletter" in user_msg.lower() or "trends" in user_msg.lower():
                return type('obj', (object,), {'content': json.dumps({
                    "classification": "newsletter",
                    "confidence": 0.96,
                    "reasoning": "E-Mail ist ein Newsletter"
                })})
            elif "termin" in user_msg.lower() or "meeting" in user_msg.lower():
                return type('obj', (object,), {'content': json.dumps({
                    "classification": "appointment",
                    "confidence": 0.94,
                    "reasoning": "E-Mail ist eine Terminanfrage"
                })})

        # Generische freundliche Antwort
        return type('obj', (object,), {'content':
            "Vielen Dank für Ihre Anfrage! Ich habe Ihre E-Mail analysiert und die relevanten Informationen verarbeitet. "
            "Bei weiteren Fragen stehe ich Ihnen gerne zur Verfügung."
        })


class LLMClient:
    """Zentraler LLM-Client für das Agentensystem"""

    def __init__(self):
        """Initialisiert den Ollama-Client mit Fallback auf Mock"""
        self.use_mock = False
        try:
            self.llm = ChatOllama(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=0.7,
            )
            logger.info(f"LLM Client initialisiert: {settings.ollama_model} @ {settings.ollama_base_url}")
        except Exception as e:
            logger.warning(f"Ollama nicht verfügbar, verwende Mock-LLM: {str(e)}")
            self.llm = MockLLM()
            self.use_mock = True

    def invoke(self, system_prompt: str, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        Ruft das LLM mit einem System-Prompt und User-Message auf

        Args:
            system_prompt: Der System-Prompt für die Agentenrolle
            user_message: Die User-Nachricht
            context: Optional zusätzlicher Kontext als Dictionary

        Returns:
            Die generierte Antwort als String
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
            ]

            # Optional: Kontext hinzufügen
            if context:
                context_str = "\n\nZusätzlicher Kontext:\n"
                for key, value in context.items():
                    context_str += f"- {key}: {value}\n"
                messages.append(SystemMessage(content=context_str))

            messages.append(HumanMessage(content=user_message))

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Fehler beim LLM-Aufruf: {str(e)}")
            raise

    def invoke_with_history(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """
        Ruft das LLM mit Chat-Historie auf

        Args:
            system_prompt: Der System-Prompt
            messages: Liste von Chat-Nachrichten mit role und content

        Returns:
            Die generierte Antwort
        """
        try:
            formatted_messages = [SystemMessage(content=system_prompt)]

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "user":
                    formatted_messages.append(HumanMessage(content=content))
                elif role == "assistant" or role == "agent":
                    formatted_messages.append(AIMessage(content=content))

            response = self.llm.invoke(formatted_messages)
            return response.content

        except Exception as e:
            logger.error(f"Fehler beim LLM-Aufruf mit Historie: {str(e)}")
            raise


# Singleton Instance
llm_client = LLMClient()
