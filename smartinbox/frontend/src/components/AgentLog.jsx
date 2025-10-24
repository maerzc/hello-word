/**
 * Agent-Log-Komponente
 * Zeigt die Schritte aller Agenten visuell an
 */

import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function AgentLog({ steps }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} style={{ color: '#10b981' }} />;
      case 'failed':
        return <XCircle size={16} style={{ color: '#ef4444' }} />;
      case 'started':
        return <Clock size={16} style={{ color: '#fbbf24' }} />;
      default:
        return <Activity size={16} />;
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="card">
      <h2>
        <Activity size={20} />
        Agenten-Aktivität
      </h2>

      <div className="agent-steps">
        {steps.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#718096', padding: '2rem' }}>
            Noch keine Agenten-Aktivität
          </div>
        ) : (
          steps.map((step, index) => (
            <div
              key={index}
              className={`agent-step ${step.status}`}
            >
              <div className="agent-step-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {getStatusIcon(step.status)}
                  <span className="agent-name">{step.agent_name}</span>
                </div>
                <span className={`agent-status ${step.status}`}>
                  {step.status === 'completed' ? 'Abgeschlossen' :
                   step.status === 'failed' ? 'Fehlgeschlagen' :
                   'In Bearbeitung'}
                </span>
              </div>

              <div className="agent-details">
                {step.details}
              </div>

              <div style={{ fontSize: '0.75rem', color: '#718096', marginTop: '0.5rem' }}>
                {formatTimestamp(step.timestamp)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
