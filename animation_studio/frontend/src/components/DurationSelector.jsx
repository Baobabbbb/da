import React from 'react';
import './Components.css';

const DurationSelector = ({ durations, selectedDuration, onDurationSelect, formatDuration }) => {
  return (
    <div className="duration-selector">
      <div className="duration-options">
        {durations.map((duration, index) => (
          <button
            key={duration}
            className={`duration-option ${selectedDuration === duration ? 'selected' : ''}`}
            onClick={() => onDurationSelect(duration)}
          >
            {formatDuration(duration)}
          </button>
        ))}
      </div>
    </div>
  );
};

export default DurationSelector;
