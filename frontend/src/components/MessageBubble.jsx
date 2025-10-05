import React from 'react';

const MessageBubble = ({ message, characters }) => {
  const character = characters.find(char => char.id === message.characterId);
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-bubble ${isUser ? 'user-message' : 'character-message'}`}>
      {!isUser && character && (
        <div className="message-avatar">
          <img src={character.images[0]} alt={character.name} />
        </div>
      )}
      <div className="message-content">
        {!isUser && character && (
          <div className="message-header">
            <span className="character-name">{character.name}</span>
            <span className="timestamp">{message.timestamp}</span>
          </div>
        )}
        <div className="message-text">{message.content}</div>
      </div>
    </div>
  );
};

export default MessageBubble;