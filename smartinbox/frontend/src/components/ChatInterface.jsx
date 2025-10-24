/**
 * Chat-Interface-Komponente
 * Zeigt Chat-Nachrichten und ermöglicht Benutzereingaben
 */

import { useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';

export default function ChatInterface({ messages, onSendMessage, isLoading }) {
  const [inputMessage, setInputMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="card">
      <h2>
        <MessageSquare size={20} />
        Chat-Assistent
      </h2>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#718096', padding: '2rem' }}>
            Noch keine Nachrichten. Senden Sie eine E-Mail zur Verarbeitung.
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role}`}
            >
              <div>{msg.content}</div>
              <div className="message-timestamp">
                {formatTimestamp(msg.timestamp)}
                {msg.agent_name && ` • ${msg.agent_name}`}
              </div>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Nachricht eingeben..."
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || !inputMessage.trim()}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
