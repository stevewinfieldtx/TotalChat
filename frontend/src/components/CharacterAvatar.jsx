import React, { useState, useEffect } from 'react';
import { useImageRotation } from '../hooks/useImageRotation';

const CharacterAvatar = ({ character, isActive, isTyping }) => {
  const currentImage = useImageRotation(character.images, 5000); // Rotate every 5 seconds

  return (
    <div className={`character-avatar ${isActive ? 'active' : ''} ${isTyping ? 'typing' : ''}`}>
      <div className="avatar-container">
        <img 
          src={currentImage} 
          alt={character.name}
          className="avatar-image"
        />
        {isTyping && (
          <div className="avatar-typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>
      <div className="character-info">
        <span className="character-name">{character.name}</span>
        <span className="character-title">{character.title}</span>
      </div>
    </div>
  );
};

export default CharacterAvatar;