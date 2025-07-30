import React from 'react';
import './Components.css';

const StatusIndicator = ({ health }) => {
  if (!health) {
    return (
      <div className="status-indicator sttus-loading">
        ��� Vérification du système...
      </div>
    );
  }

  const getStatusInfo = () => {
    if (health.status === 'healthy') {
      return {
        className: 'status-healthy',
        icon: '✅',
        text: 'Système opérationnel'
      };
    } else if (health.status === 'degraded') {
      return {
        className: 'status-degraded',
        icon: '⚠️',
        text: 'Système partiellement opérationnel'
      };
    } else {
      return {
        className: 'status-unhealthy',
        icon: '❌',
        text: 'Système indisponible'
      };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className={`status-indicator ${statusInfo.className}`}>
      {statusInfo.icon} {statusInfo.text}
    </div>
  );
};

export default StatusIndicator;
