import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import CharacterAvatar from './CharacterAvatar';
import VoiceControls from './VoiceControls';
import { useChat } from '../hooks/useChat';
import { Send, Mic, MicOff, RotateCcw } from 'lucide-react';

const ChatInterface = ({ characters, onBack }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { messages, sendMessage, isTyping, currentSpeaker } = useChat(characters);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (inputMessage.trim()) {
      await sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button onClick={onBack} className="back-button">← Back</button>
        <div className="character-avatars">
          {characters.map((char, index) => (
            <CharacterAvatar 
              key={char.id}
              character={char}
              isActive={currentSpeaker?.id === char.id}
              isTyping={isTyping[char.id]}
            />
          ))}
        </div>
        <VoiceControls />
      </div>

      <div className="messages-container">
        {messages.map((message, index) => (
          <MessageBubble 
            key={index}
            message={message}
            characters={characters}
          />
        ))}
        {Object.values(isTyping).some(typing => typing) && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          className="message-input"
        />
        <button 
          onClick={handleSend}
          disabled={!inputMessage.trim()}
          className="send-button"
        >
          <Send size={20} />
        </button>
        <button 
          onClick={() => setIsVoiceMode(!isVoiceMode)}
          className={`voice-button ${isVoiceMode ? 'active' : ''}`}
        >
          {isVoiceMode ? <MicOff size={20} /> : <Mic size={20} />}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;