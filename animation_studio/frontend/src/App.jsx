import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);
  const [currentStep, setCurrentStep] = useState('theme');
  const [animationId, setAnimationId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStepText, setCurrentStepText] = useState('');
  const [result, setResult] = useState(null);
  const [costInfo, setCostInfo] = useState(null);

  const durations = [
    { value: 30, label: '30 secondes', icon: '⚡' },
    { value: 60, label: '1 minute', icon: '⏱️' },
    { value: 120, label: '2 minutes', icon: '⏰' },
    { value: 180, label: '3 minutes', icon: '🕐' },
    { value: 240, label: '4 minutes', icon: '🕑' },
    { value: 300, label: '5 minutes', icon: '🕒' }
  ];

  useEffect(() => {
    loadThemes();
    loadCosts();
  }, []);

  const loadThemes = async () => {
    try {
      const response = await fetch('http://localhost:8011/themes');
      const data = await response.json();
      setThemes(data.themes || []);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const loadCosts = async () => {
    try {
      const response = await fetch('http://localhost:8011/costs');
      const data = await response.json();
      setCostInfo(data);
    } catch (error) {
      console.error('Erreur coûts:', error);
    }
  };

  const handleThemeSelect = (themeId) => {
    setSelectedTheme(themeId);
    setCurrentStep('duration');
  };

  const handleDurationSelect = (duration) => {
    setSelectedDuration(duration);
    setCurrentStep('generate');
  };

  const handleGenerate = async () => {
    try {
      setCurrentStep('generating');
      
      const response = await fetch('http://localhost:8011/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: selectedTheme, duration: selectedDuration })
      });
      
      const data = await response.json();
      setAnimationId(data.animation_id);
      
      checkProgress(data.animation_id);
      
    } catch (error) {
      console.error('Erreur génération:', error);
    }
  };

  const checkProgress = async (id) => {
    try {
      const response = await fetch(`http://localhost:8011/status/${id}`);
      const data = await response.json();
      
      setProgress(data.progress || 0);
      setCurrentStepText(data.current_step || '');
      
      if (data.status === 'completed') {
        setResult(data.result);
        setCurrentStep('video');
      } else if (data.status === 'error') {
        console.error('Erreur:', data.error);
        setCurrentStep('generate');
      } else {
        setTimeout(() => checkProgress(id), 1500);
      }
    } catch (error) {
      console.error('Erreur vérification:', error);
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}min`;
  };

  const getThemeName = (themeId) => {
    const theme = themes.find(t => t.id === themeId);
    return theme ? theme.name : themeId;
  };

  const getThemeEmoji = (themeId) => {
    const theme = themes.find(t => t.id === themeId);
    return theme ? theme.emoji : '🎬';
  };

  const getDurationInfo = (duration) => {
    return durations.find(d => d.value === duration);
  };

  const getEstimatedCost = (duration) => {
    if (!costInfo) return null;
    const costKey = `${duration}s`;
    return costInfo.cost_estimates?.[costKey];
  };

  const restart = () => {
    setCurrentStep('theme');
    setSelectedTheme(null);
    setSelectedDuration(null);
    setAnimationId(null);
    setProgress(0);
    setResult(null);
  };

  const goBack = () => {
    if (currentStep === 'duration') {
      setCurrentStep('theme');
      setSelectedTheme(null);
    } else if (currentStep === 'generate') {
      setCurrentStep('duration');
      setSelectedDuration(null);
    }
  };

  return (
    <div className="app">
      {/* Header avec navigation des étapes */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🎬</span>
            <h1>Animation Studio</h1>
          </div>
          <div className="step-indicator">
            <div className={`step ${currentStep === 'theme' ? 'active' : ''} ${['duration', 'generate', 'generating', 'video'].includes(currentStep) ? 'completed' : ''}`}>
              <span className="step-number">1</span>
              <span className="step-label">Thème</span>
            </div>
            <div className={`step ${currentStep === 'duration' ? 'active' : ''} ${['generate', 'generating', 'video'].includes(currentStep) ? 'completed' : ''}`}>
              <span className="step-number">2</span>
              <span className="step-label">Durée</span>
            </div>
            <div className={`step ${['generate', 'generating'].includes(currentStep) ? 'active' : ''} ${currentStep === 'video' ? 'completed' : ''}`}>
              <span className="step-number">3</span>
              <span className="step-label">Génération</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main">
        
        {/* Étape 1: Choix du thème */}
        {currentStep === 'theme' && (
          <div className="section theme-section">
            <div className="section-header">
              <h2>🎨 Choisissez votre univers</h2>
              <p>Découvrez des thèmes magiques pour créer des histoires captivantes</p>
            </div>
            
            <div className="themes-grid">
              {themes.map(theme => (
                <div 
                  key={theme.id}
                  className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
                  onClick={() => handleThemeSelect(theme.id)}
                >
                  <div className="theme-emoji">{theme.emoji}</div>
                  <h3>{theme.name}</h3>
                  <div className="theme-hover-effect"></div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Étape 2: Choix de la durée */}
        {currentStep === 'duration' && (
          <div className="section duration-section">
            <div className="section-header">
              <button className="back-button" onClick={goBack}>
                ← Retour
              </button>
              <h2>⏱️ Choisissez la durée</h2>
              <p>Combien de temps durera votre animation ?</p>
            </div>
            
            <div className="selected-theme-display">
              <span className="theme-emoji">{getThemeEmoji(selectedTheme)}</span>
              <span className="theme-name">{getThemeName(selectedTheme)}</span>
            </div>
            
            <div className="duration-options">
              {durations.map(duration => (
                <div
                  key={duration.value}
                  className={`duration-card ${selectedDuration === duration.value ? 'selected' : ''}`}
                  onClick={() => handleDurationSelect(duration.value)}
                >
                  <div className="duration-icon">{duration.icon}</div>
                  <div className="duration-info">
                    <h3>{duration.label}</h3>
                    {getEstimatedCost(duration.value) && (
                      <p className="cost-info">
                        ~{getEstimatedCost(duration.value).total_estimated_cost.toFixed(2)}€
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Étape 3: Prêt à générer */}
        {currentStep === 'generate' && (
          <div className="section generate-section">
            <div className="section-header">
              <button className="back-button" onClick={goBack}>
                ← Retour
              </button>
              <h2>🚀 Prêt à créer !</h2>
              <p>Votre animation va prendre vie</p>
            </div>
            
            <div className="generation-summary">
              <div className="summary-card">
                <div className="summary-item">
                  <span className="summary-icon">{getThemeEmoji(selectedTheme)}</span>
                  <div className="summary-text">
                    <h3>Thème</h3>
                    <p>{getThemeName(selectedTheme)}</p>
                  </div>
                </div>
                
                <div className="summary-item">
                  <span className="summary-icon">{getDurationInfo(selectedDuration)?.icon}</span>
                  <div className="summary-text">
                    <h3>Durée</h3>
                    <p>{getDurationInfo(selectedDuration)?.label}</p>
                  </div>
                </div>
                
                {getEstimatedCost(selectedDuration) && (
                  <div className="summary-item">
                    <span className="summary-icon">💰</span>
                    <div className="summary-text">
                      <h3>Coût estimé</h3>
                      <p>{getEstimatedCost(selectedDuration).total_estimated_cost.toFixed(2)}€</p>
                    </div>
                  </div>
                )}
              </div>
              
              <button className="generate-button" onClick={handleGenerate}>
                <span className="button-icon">🎬</span>
                <span className="button-text">Créer l'animation</span>
              </button>
            </div>
          </div>
        )}

        {/* Étape 4: Génération en cours */}
        {currentStep === 'generating' && (
          <div className="section generating-section">
            <div className="section-header">
              <h2>🎬 Création en cours...</h2>
              <p>L'IA travaille pour créer votre dessin animé</p>
            </div>
            
            <div className="generation-progress">
              <div className="progress-animation">
                <div className="loading-spinner"></div>
              </div>
              
              <div className="progress-container">
                <div className="progress-text">{currentStepText}</div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <div className="progress-percentage">{progress}%</div>
              </div>
              
              <div className="progress-tips">
                <p>💡 Conseil : La génération peut prendre 5-10 minutes selon la durée</p>
              </div>
            </div>
          </div>
        )}

        {/* Étape 5: Vidéo finale */}
        {currentStep === 'video' && result && (
          <div className="section video-section">
            <div className="section-header">
              <h2>🎉 Animation terminée !</h2>
              <p>Votre dessin animé est prêt</p>
            </div>
            
            <div className="video-result">
              <div className="video-player">
                <video 
                  src={result.final_video_url} 
                  controls 
                  poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='400' viewBox='0 0 600 400'%3E%3Crect width='600' height='400' fill='%23f0f0f0'/%3E%3Ctext x='300' y='200' text-anchor='middle' font-size='24' fill='%23999'%3EChargement...%3C/text%3E%3C/svg%3E"
                >
                  Votre navigateur ne supporte pas les vidéos.
                </video>
              </div>
              
              <div className="video-info">
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-icon">{getThemeEmoji(selectedTheme)}</span>
                    <div className="info-text">
                      <h4>Thème</h4>
                      <p>{getThemeName(selectedTheme)}</p>
                    </div>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-icon">⏱️</span>
                    <div className="info-text">
                      <h4>Durée</h4>
                      <p>{formatDuration(selectedDuration)}</p>
                    </div>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-icon">🎬</span>
                    <div className="info-text">
                      <h4>Qualité</h4>
                      <p>HD 16:9</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="video-actions">
                <button onClick={restart} className="restart-button">
                  <span className="button-icon">🔄</span>
                  <span className="button-text">Créer une nouvelle animation</span>
                </button>
                
                <button 
                  onClick={() => window.open(result.final_video_url, '_blank')} 
                  className="download-button"
                >
                  <span className="button-icon">⬇️</span>
                  <span className="button-text">Télécharger</span>
                </button>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App; 