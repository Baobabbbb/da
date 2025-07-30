import React from 'react';
import './Components.css';

const ThemeSelector = ({ themes, selectedTheme, onThemeSelect }) => {
  const themeKeys = Object.keys(themes);

  if (themeKeys.length === 0) {
    return (
      <div className="themes-loading">
        <p>Chargement des thèmes...</p>
      </div>
    );
  }

  return (
    <div className="themes-container">
      <div className="themes-grid">
        {themeKeys.map((themeKey) => {
          const theme = themes[themeKey];
          const isSelected = selectedTheme === themeKey;
          
          return (
            <div
              key={themeKey}
              className={`theme-card ${isSelected ? 'selected' : ''}`}
              onClick={() => onThemeSelect(themeKey)}
            >
              <div className="theme-icon">{theme.icon || '���'}</div>
              <h3 className="theme-name">{theme.name}</h3>
              <p className="theme-description">{theme.description}</p>
              <div className="theme-elements">
                <small>{theme.elements || ''}</small>
              </div>
              
              {isSelected && (
                <div className="selection-indicator">
                  ✓
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThemeSelector;
