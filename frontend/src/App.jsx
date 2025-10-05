import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import CharacterSelector from './components/CharacterSelector';
import './styles/globals.css';

function App() {
  const [selectedCharacters, setSelectedCharacters] = useState([]);
  const [isChatActive, setIsChatActive] = useState(false);

  return (
    <div className="app">
      <div className="app-header">
        <h1>📚 Literary Character Chat</h1>
        <p>Converse with up to 3 characters from history & literature</p>
      </div>
      
      {!isChatActive ? (
        <CharacterSelector 
          onSelectionComplete={(characters) => {
            setSelectedCharacters(characters);
            setIsChatActive(true);
          }}
        />
      ) : (
        <ChatInterface 
          characters={selectedCharacters}
          onBack={() => setIsChatActive(false)}
        />
      )}
    </div>
  );
}

export default App;