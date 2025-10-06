import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import CharacterSelector from './components/CharacterSelector';
import AdminPanel from './components/AdminPanel';
import './styles/globals.css';

function App() {
  const [selectedCharacters, setSelectedCharacters] = useState([]);
  const [isChatActive, setIsChatActive] = useState(false);
  const [showAdmin, setShowAdmin] = useState(true);

  return (
    <div className="app">
      <div className="app-header">
        <h1>📚 Literary Character Chat</h1>
        <p>Converse with up to 3 characters from history & literature</p>
      </div>
      
      {!isChatActive ? (
        <div style={{ display: 'grid', gap: 16 }}>
          {showAdmin && (
            <AdminPanel onUseSelection={(chars) => {
              setSelectedCharacters(chars);
              setIsChatActive(true);
            }} />
          )}
          <CharacterSelector 
            onSelectionComplete={(characters) => {
              setSelectedCharacters(characters);
              setIsChatActive(true);
            }}
          />
        </div>
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