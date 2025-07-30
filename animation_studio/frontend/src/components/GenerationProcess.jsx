import './Components.css';
import React, { useState, useEffect } from 'react';
import animationService from '../services/animationService.js';

const GenerationProcess = ({ theme, duration, themeName, themeIcon, animationId, onComplete, onError }) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('🚀 Initialisation...');
  const [status, setStatus] = useState('starting');

  useEffect(() => {
    if (!animationId) return;

    const checkProgress = async () => {
      try {
        const statusData = await animationService.getAnimationStatus(animationId);
        
        setProgress(statusData.progress);
        setCurrentStep(statusData.current_step);
        setStatus(statusData.status);

        if (statusData.status === 'completed') {
          onComplete && onComplete(statusData.result);
        } else if (statusData.status === 'error') {
          onError && onError(statusData.error);
        } else {
          // Continuer à vérifier le progrès
          setTimeout(checkProgress, 1500);
        }
      } catch (error) {
        console.error('Erreur vérification progression:', error);
        onError && onError('Erreur de connexion au serveur');
      }
    };

    // Démarrer la vérification après 1 seconde
    const timer = setTimeout(checkProgress, 1000);
    
    return () => clearTimeout(timer);
  }, [animationId, onComplete, onError]);

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}min${seconds % 60 ? ` ${seconds % 60}s` : ''}`;
  };

  return (
    <div className="generation-container">
      <div className="generation-header">
        <div className="generation-icon">
          {themeIcon || '🎬'}
        </div>
        <h2>Création de votre animation {themeName}</h2>
        <p>Durée: {formatDuration(duration)} • Thème: {themeName}</p>
      </div>

      <div className="generation-progress">
        <div className="progress-info">
          <span className="progress-text">{currentStep}</span>
          <span className="progress-percentage">{progress}%</span>
        </div>
        
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
          <div className="progress-shimmer" />
        </div>
      </div>

      <div className="generation-details">
        <div className="generation-stats">
          <div className="stat-item">
            <span className="stat-label">🤖 IA utilisées</span>
            <span className="stat-value">OpenAI + Wavespeed + FAL</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">🎯 Statut</span>
            <span className="stat-value">
              {status === 'starting' && '🚀 Démarrage'}
              {status === 'generating' && '⚡ Génération'}
              {status === 'completed' && '✅ Terminé'}
              {status === 'error' && '❌ Erreur'}
            </span>
          </div>
        </div>

        <div className="generation-tips">
          <div className="tip">
            💡 <strong>Le saviez-vous ?</strong> Nos IA créent des animations uniques à chaque fois !
          </div>
        </div>
      </div>

      <div className="generation-animation">
        <div className="floating-elements">
          <div className="floating-emoji">🎬</div>
          <div className="floating-emoji">🎨</div>
          <div className="floating-emoji">✨</div>
          <div className="floating-emoji">🎵</div>
        </div>
      </div>
    </div>
  );
};

export default GenerationProcess;
