/**
 * Mail-Inbox-Komponente
 * Ermöglicht das Einfügen und Simulieren von E-Mails
 */

import { useState } from 'react';
import { Mail, Send, FileJson } from 'lucide-react';

// Beispiel-E-Mails für schnelles Testen
const EXAMPLE_EMAILS = [
  {
    sender: 'kunde@example.com',
    subject: 'Angebotsanfrage Cloud-Hosting',
    body: 'Guten Tag,\n\nich interessiere mich für Ihr Cloud-Hosting Angebot. Wir benötigen eine Lösung für ca. 50 Mitarbeiter mit etwa 500GB Speicher.\n\nKönnen Sie uns bitte ein Angebot unterbreiten?\n\nMit freundlichen Grüßen'
  },
  {
    sender: 'buchhaltung@firma.de',
    subject: 'Rechnung RE-2025-001',
    body: 'Sehr geehrte Damen und Herren,\n\nanbei erhalten Sie unsere Rechnung RE-2025-001 vom 15.01.2025.\n\nRechnungsbetrag: 1.499,00 EUR\nZahlungsziel: 14 Tage\n\nMit freundlichen Grüßen\nBuchhaltung'
  },
  {
    sender: 'support@kunde.com',
    subject: 'Hilfe - Kann mich nicht einloggen',
    body: 'Hallo Support-Team,\n\nich habe Probleme beim Login. Meine E-Mail ist support@kunde.com aber das Passwort funktioniert nicht.\n\nKönnen Sie mir helfen?\n\nDanke!'
  },
  {
    sender: 'newsletter@techblog.com',
    subject: 'TechBlog Newsletter - KI-Trends 2025',
    body: '📰 TechBlog Newsletter\n\nTop-Themen diese Woche:\n• KI-Agenten revolutionieren die Automatisierung\n• Neue LangGraph-Features vorgestellt\n• Cloud-Native wird zum Standard\n\nLesen Sie mehr auf techblog.com\n\nAbmelden: newsletter.techblog.com/unsubscribe'
  },
  {
    sender: 'interessent@business.de',
    subject: 'Terminanfrage Beratungsgespräch',
    body: 'Guten Tag,\n\nich würde gerne einen Beratungstermin mit Ihnen vereinbaren. Es geht um die Einführung eines KI-Agentensystems in unserem Unternehmen.\n\nIch wäre nächste Woche Dienstag oder Donnerstag verfügbar.\n\nBeste Grüße'
  }
];

export default function MailInbox({ onProcessEmail, isLoading, classification }) {
  const [sender, setSender] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (sender && subject && body && !isLoading) {
      onProcessEmail({ sender, subject, body });
    }
  };

  const loadExample = (index) => {
    const example = EXAMPLE_EMAILS[index];
    setSender(example.sender);
    setSubject(example.subject);
    setBody(example.body);
  };

  const clearForm = () => {
    setSender('');
    setSubject('');
    setBody('');
  };

  const getClassificationLabel = (classification) => {
    const labels = {
      'quote_request': 'Angebotsanfrage',
      'invoice': 'Rechnung',
      'support': 'Support',
      'newsletter': 'Newsletter',
      'appointment': 'Termin'
    };
    return labels[classification] || classification;
  };

  return (
    <div className="card">
      <h2>
        <Mail size={20} />
        E-Mail Simulation
      </h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="sender">Absender</label>
          <input
            id="sender"
            type="email"
            value={sender}
            onChange={(e) => setSender(e.target.value)}
            placeholder="absender@example.com"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="subject">Betreff</label>
          <input
            id="subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="E-Mail Betreff"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="body">Nachricht</label>
          <textarea
            id="body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="E-Mail Inhalt..."
            required
            disabled={isLoading}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !sender || !subject || !body}
          >
            <Send size={18} />
            {isLoading ? 'Verarbeite...' : 'E-Mail verarbeiten'}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={clearForm}
            disabled={isLoading}
          >
            Zurücksetzen
          </button>
        </div>
      </form>

      {classification && (
        <div className="classification-badge">
          <FileJson size={16} />
          Klassifiziert als: {getClassificationLabel(classification)}
        </div>
      )}

      <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #e2e8f0' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem', color: '#4a5568' }}>
          Beispiel-E-Mails
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {EXAMPLE_EMAILS.map((email, index) => (
            <button
              key={index}
              type="button"
              className="btn btn-secondary"
              onClick={() => loadExample(index)}
              disabled={isLoading}
              style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}
            >
              {email.subject.substring(0, 20)}...
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
