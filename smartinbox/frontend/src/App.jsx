/**
 * SmartInbox Hauptkomponente
 * Integriert alle Komponenten und verwaltet den State
 */

import { useState } from 'react';
import './App.css';
import MailInbox from './components/MailInbox';
import ChatInterface from './components/ChatInterface';
import AgentLog from './components/AgentLog';
import { processEmail, sendChatMessage } from './services/api';
import { Mail, Bot } from 'lucide-react';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [classification, setClassification] = useState(null);
  const [agentSteps, setAgentSteps] = useState([]);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  const handleProcessEmail = async (emailData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await processEmail(emailData);

      setClassification(result.classification);
      setAgentSteps(result.agent_steps || []);
      setMessages(result.messages || []);

      // Wenn es eine finale Antwort gibt, zur Chat-Historie hinzufügen
      if (result.final_response && result.messages.length === 0) {
        setMessages([{
          role: 'assistant',
          content: result.final_response,
          timestamp: new Date().toISOString(),
          agent_name: 'System'
        }]);
      }

      if (result.error) {
        setError(result.error);
      }
    } catch (err) {
      console.error('Fehler beim Verarbeiten der E-Mail:', err);
      setError('Fehler beim Verarbeiten der E-Mail. Bitte prüfen Sie, ob das Backend läuft.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message) => {
    setIsLoading(true);
    setError(null);

    // User-Nachricht sofort zur Historie hinzufügen
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      agent_name: null
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const result = await sendChatMessage(message);

      // Antwort zur Historie hinzufügen
      const assistantMessage = {
        role: 'assistant',
        content: result.response,
        timestamp: result.timestamp,
        agent_name: 'ChatAgent'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Fehler beim Senden der Chat-Nachricht:', err);
      setError('Fehler beim Senden der Nachricht.');

      // Fehlermeldung zur Historie hinzufügen
      const errorMessage = {
        role: 'assistant',
        content: 'Entschuldigung, es gab einen Fehler beim Verarbeiten Ihrer Nachricht.',
        timestamp: new Date().toISOString(),
        agent_name: 'System'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>
          <Bot size={32} style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '0.5rem' }} />
          SmartInbox Agentensystem
        </h1>
        <p>KI-gestützte E-Mail-Verarbeitung mit spezialisierten Agenten</p>
      </header>

      <div className="main-container">
        <div className="email-section">
          <MailInbox
            onProcessEmail={handleProcessEmail}
            isLoading={isLoading}
            classification={classification}
          />

          <AgentLog steps={agentSteps} />

          {error && (
            <div className="card" style={{ background: '#fee2e2', borderColor: '#ef4444' }}>
              <h2 style={{ color: '#991b1b' }}>Fehler</h2>
              <p style={{ color: '#991b1b' }}>{error}</p>
            </div>
          )}
        </div>

        <div className="chat-section">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
