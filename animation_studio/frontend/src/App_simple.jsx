import React, { useState, useEffect } from 'react';
import ThemeSelector from './components/ThemeSelector.jsx';
import DurationSelector from './components/DurationSelector.jsx';
import GenerationProcess from './components/GenerationProcess.jsx';
import VideoPlayer from './components/VideoPlayer.jsx';
import StatusIndicator from './components/StatusIndicator.jsx';
import animationService from './services/animationService.js';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('theme');
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState(null);
  const [themes, setThemes] = useState([]);
  const [durations] = useState([30, 60, 120, 180, 240, 300]);
  const [generationResult, setGenerationResult] = useState(null);
  const [animationId, setAnimationId] = useState(null);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);

  useEffect(() => {
    loadThemes();
    checkApiHealth();
  }, []);

  const loadThemes = async () => {
    try {
      const data = await animationService.getThemes();
      setThemes(data.themes || []);
    } catch (error) {
      console.error('Erreur lors du chargement des thèmes:', error);
      setError('Impossible de charger les thèmes');
    }
  };

  const checkApiHealth = async () => {
    try {
      const health = await animationService.checkHealth();
      setApiHealth(health);
    } catch (error) {
      console.error('Erreur de santé API:', error);
      setApiHealth({ status: 'unhealthy' });
    }
  };

  const handleThemeSelect = (themeId) => {
    setSelectedTheme(themeId);
    if (selectedDuration) {
      setCurrentStep('generate');
    } else {
      setCurrentStep('duration');
    }
  };

  const handleDurationSelect = (duration) => {
    setSelectedDuration(duration);
    if (selectedTheme) {
      setCurrentStep('generate');
    }
  };

  const handleStartGeneration = async () => {
    try {
      setCurrentStep('generating');
      setError(null);
      
      const response = await animationService.generateAnimation({
        theme: selectedTheme,
        duration: selectedDuration
      });
      
      setAnimationId(response.animation_id);
    } catch (error) {
      console.error('Erreur génération:', error);
      setError('Erreur lors du lancement de la génération');
      setCurrentStep('generate');
    }
  };

  const handleGenerationComplete = (result) => {
    setGenerationResult(result);
    setCurrentStep('video');
  };

  const handleGenerationError = (errorMsg) => {
    setError(errorMsg);
    setCurrentStep('generate');
  };

  const handleRestart = () => {
    setCurrentStep('theme');
    setSelectedTheme(null);
    setSelectedDuration(null);
    setGenerationResult(null);
    setAnimationId(null);
    setError(null);
  };

  const getSelectedTheme = () => themes.find(t => t.id === selectedTheme);

  return (
    <div className="app">
      <StatusIndicator health={apiHealth} />
      
      <header className="header">
        <div className="header-content">
          <h1 className="title">
            🎬 Animation Studio
          </h1>
          <p className="subtitle">
            Créez des dessins animés magiques pour enfants avec l'IA
          </p>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="error-banner">
            ❌ {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {currentStep === 'theme' && (
          <div className="section">
            <h2>🎨 Choisissez un thème</h2>
            <ThemeSelector 
              themes={themes}
              selectedTheme={selectedTheme}
              onThemeSelect={handleThemeSelect}
            />
          </div>
        )}

        {currentStep === 'duration' && (
          <div className="section">
            <h2>⏱️ Choisissez la durée</h2>
            <DurationSelector 
              durations={durations}
              selectedDuration={selectedDuration}
              onDurationSelect={handleDurationSelect}
            />
          </div>
        )}

        {currentStep === 'generate' && (
          <div className="section">
            <h2>🚀 Prêt à générer !</h2>
            <div className="generation-summary">
              <p><strong>Thème:</strong> {getSelectedTheme()?.name}</p>
              <p><strong>Durée:</strong> {selectedDuration}s</p>
            </div>
            <button 
              className="generate-button"
              onClick={handleStartGeneration}
            >
              🎬 Générer l'animation
            </button>
          </div>
        )}

        {currentStep === 'generating' && (
          <GenerationProcess 
            theme={selectedTheme}
            duration={selectedDuration}
            themeName={getSelectedTheme()?.name}
            themeIcon={getSelectedTheme()?.icon}
            animationId={animationId}
            onComplete={handleGenerationComplete}
            onError={handleGenerationError}
          />
        )}

        {currentStep === 'video' && generationResult && (
          <VideoPlayer 
            result={generationResult}
            theme={getSelectedTheme()?.name}
            duration={selectedDuration}
            onRestart={handleRestart}
          />
        )}
      </main>
    </div>
  );
}

export default App; 