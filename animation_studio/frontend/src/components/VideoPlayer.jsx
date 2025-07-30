import './Components.css';
import React, { useState } from 'react';
import { motion } from 'framer-motion';

const VideoPlayer = ({ result, onStartOver, themeName, duration }) => {
  const [isVideoLoaded, setIsVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState(false);

  const handleVideoLoad = () => {
    setIsVideoLoaded(true);
  };

  const handleVideoError = () => {
    setVideoError(true);
  };

  const handleDownload = () => {
    if (result.final_video_url) {
      const link = document.createElement('a');
      link.href = result.final_video_url;
      link.download = `animation-${themeName}-${duration}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleShare = async () => {
    if (navigator.share && result.final_video_url) {
      try {
        await navigator.share({
          title: 'Mon dessin animé',
          text: `Regardez ce super dessin animé sur le thème "${themeName}" !`,
          url: result.final_video_url,
        });
      } catch (error) {
        console.log('Erreur lors du partage:', error);
      }
    } else {
      // Fallback: copier l'URL dans le presse-papiers
      if (result.final_video_url) {
        navigator.clipboard.writeText(result.final_video_url);
        alert('Lien copié dans le presse-papiers !');
      }
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m${remainingSeconds}s` : `${minutes}m`;
  };

  if (!result) {
    return (
      <motion.div 
        className="video-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="no-video">
          <h2>🎬 Créez votre premier dessin animé !</h2>
          <p>Sélectionnez un thème et une durée pour commencer la magie...</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="video-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.h1 
        className="video-title"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        🎉 Votre dessin animé est prêt !
      </motion.h1>

      <motion.div 
        className="video-info"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <p><strong>Thème:</strong> {themeName}</p>
        <p><strong>Durée:</strong> {formatDuration(duration)}</p>
        {result.generation_time && (
          <p><strong>Temps de génération:</strong> {Math.round(result.generation_time)}s</p>
        )}
      </motion.div>

      <motion.div 
        className="video-player"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4 }}
      >
        {result.final_video_url ? (
          <>
            {!isVideoLoaded && !videoError && (
              <div className="video-loading">
                <div className="loading-spinner"></div>
                <p>Chargement de la vidéo...</p>
              </div>
            )}
            
            {videoError && (
              <div className="video-error">
                <p>❌ Erreur lors du chargement de la vidéo</p>
                <p>URL: {result.final_video_url}</p>
              </div>
            )}
            
            <video
              controls
              onLoadedData={handleVideoLoad}
              onError={handleVideoError}
              style={{ 
                display: isVideoLoaded && !videoError ? 'block' : 'none',
                width: '100%',
                height: 'auto'
              }}
            >
              <source src={result.final_video_url} type="video/mp4" />
              Votre navigateur ne supporte pas la lecture vidéo.
            </video>
          </>
        ) : (
          <div className="video-loading">
            <div className="loading-spinner"></div>
            <p>Génération en cours...</p>
          </div>
        )}
      </motion.div>

      <motion.div 
        className="video-actions"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <motion.button
          onClick={onStartOver}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '25px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem',
            margin: '0.5rem'
          }}
        >
          🎬 Créer un nouveau dessin animé
        </motion.button>

        {result.final_video_url && (
          <>
            <motion.button
              onClick={handleDownload}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '25px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1rem',
                margin: '0.5rem'
              }}
            >
              📥 Télécharger
            </motion.button>

            <motion.button
              onClick={handleShare}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '25px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1rem',
                margin: '0.5rem'
              }}
            >
              📤 Partager
            </motion.button>
          </>
        )}
      </motion.div>

      {result.story_idea && (
        <motion.div 
          className="story-details"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <h3>📖 Histoire de votre animation</h3>
          <p className="story-idea">"{result.story_idea.idea}"</p>
          <p className="story-caption">{result.story_idea.caption}</p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default VideoPlayer;
      
