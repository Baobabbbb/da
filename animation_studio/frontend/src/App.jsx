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

  const durations = [30, 60, 120, 180, 240, 300];

  useEffect(() => {
    loadThemes();
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
      
      // Vérifier le progrès
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
        // Continuer à vérifier
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

  const restart = () => {
    setCurrentStep('theme');
    setSelectedTheme(null);
    setSelectedDuration(null);
    setAnimationId(null);
    setProgress(0);
    setResult(null);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎬 Animation Studio</h1>
        <p>Créez des dessins animés magiques pour enfants avec l'IA</p>
      </header>

      <main className="main">
        
        {/* Étape 1: Choix du thème */}
        {currentStep === 'theme' && (
          <div className="section">
            <h2>🎨 Choisissez un thème</h2>
            <div className="themes-grid">
              {themes.map(theme => (
                <div 
                  key={theme.id}
                  className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
                  onClick={() => handleThemeSelect(theme.id)}
                >
                  <div className="theme-icon">{theme.icon}</div>
                  <h3>{theme.name}</h3>
                  <p>{theme.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Étape 2: Choix de la durée */}
        {currentStep === 'duration' && (
          <div className="section">
            <h2>⏱️ Choisissez la durée</h2>
            <div className="duration-options">
              {durations.map(duration => (
                <button
                  key={duration}
                  className={`duration-option ${selectedDuration === duration ? 'selected' : ''}`}
                  onClick={() => handleDurationSelect(duration)}
                >
                  {formatDuration(duration)}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Étape 3: Prêt à générer */}
        {currentStep === 'generate' && (
          <div className="section">
            <h2>🚀 Prêt à générer !</h2>
            <div className="summary">
              <p><strong>Thème:</strong> {getThemeName(selectedTheme)}</p>
              <p><strong>Durée:</strong> {formatDuration(selectedDuration)}</p>
            </div>
            <button className="generate-button" onClick={handleGenerate}>
              🎬 Générer l'animation
            </button>
          </div>
        )}

        {/* Étape 4: Génération en cours */}
        {currentStep === 'generating' && (
          <div className="section">
            <h2>🎬 Création en cours...</h2>
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
          </div>
        )}

        {/* Étape 5: Vidéo finale */}
        {currentStep === 'video' && result && (
          <div className="section">
            <h2>🎉 Animation terminée !</h2>
            <div className="video-container">
              <video 
                src={result.final_video_url} 
                controls 
                width="600" 
                height="400"
              >
                Votre navigateur ne supporte pas les vidéos.
              </video>
              <div className="video-info">
                <p><strong>Thème:</strong> {getThemeName(selectedTheme)}</p>
                <p><strong>Durée:</strong> {formatDuration(selectedDuration)}</p>
              </div>
              <button onClick={restart} className="restart-button">
                🔄 Créer une nouvelle animation
              </button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App; 