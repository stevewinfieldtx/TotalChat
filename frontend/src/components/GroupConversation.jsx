// frontend/src/components/GroupConversation.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Users, MessageCircle, Volume2, VolumeX } from 'lucide-react';

const GroupConversation = ({ conversationId, characters, userId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState({});
  const [speakingCharacters, setSpeakingCharacters] = useState([]);
  const [conversationTopic, setConversationTopic] = useState('');
  const messagesEndRef = useRef(null);

  // WebSocket connection for real-time group conversation
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/group/${conversationId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'character_response') {
        // Add character response to messages
        setMessages(prev => [...prev, {
          id: Date.now(),
          speaker: data.character_id,
          content: data.content,
          timestamp: data.timestamp,
          is_user: false,
          style: data.style,
          interruption: data.interruption
        }]);
        
        // Handle simultaneous responses
        if (data.simultaneous_responses) {
          data.simultaneous_responses.forEach(response => {
            setTimeout(() => {
              setMessages(prev => [...prev, {
                id: Date.now() + Math.random(),
                speaker: response.character_id,
                content: response.content,
                timestamp: response.timestamp,
                is_user: false,
                style: response.style,
                interruption: response.interruption
              }]);
            }, response.delay || 0);
          });
        }
      }
      
      if (data.type === 'typing_indicator') {
        setIsTyping(prev => ({
          ...prev,
          [data.character_id]: data.is_typing
        }));
      }
    };

    return () => ws.close();
  }, [conversationId]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      speaker: userId,
      content: inputMessage,
      timestamp: new Date().toISOString(),
      is_user: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Send to backend
    await fetch(`http://localhost:8000/api/group/${conversationId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        speaker_id: userId,
        message: inputMessage
      })
    });
  };

  const MessageBubble = ({ message, character }) => {
    const isInterruption = message.interruption;
    const isSimultaneous = message.style?.includes('simultaneous');

    return (
      <div className={`message-bubble mb-3 ${isInterruption ? 'opacity-75 border-l-4 border-red-400' : ''} ${isSimultaneous ? 'ml-4' : ''}`}>
        <div className="flex items-start gap-3">
          <img 
            src={character?.avatar || '/default-avatar.png'}
            alt={character?.name || 'User'}
            className="w-8 h-8 rounded-full"
          />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-sm">{character?.name || 'You'}</span>
              {isInterruption && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                  interrupted
                </span>
              )}
            </div>
            <div className="bg-gray-100 rounded-lg p-3">
              {message.content}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="group-conversation bg-white rounded-lg shadow-lg h-full flex flex-col">
      <div className="conversation-header p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users size={24} />
            <div>
              <h3 className="font-semibold">Group Conversation</h3>
              <p className="text-sm text-gray-600">
                {characters.map(char => char.name).join(', ')}
              </p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Topic: {conversationTopic || 'General Discussion'}
          </div>
        </div>
      </div>

      <div className="messages-container flex-1 overflow-y-auto p-4">
        {messages.map(message => {
          const character = characters.find(char => char.id === message.speaker);
          return (
            <MessageBubble 
              key={message.id} 
              message={message} 
              character={character}
            />
          );
        })}
        
        {/* Typing indicators */}
        <div className="typing-indicators">
          {characters.map(char => 
            isTyping[char.id] && (
              <div key={char.id} className="flex items-center gap-2 mb-2 opacity-50">
                <img src={char.avatar} alt={char.name} className="w-6 h-6 rounded-full" />
                <span className="text-sm">{char.name} is typing...</span>
              </div>
            )
          )}
        </div>
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Join the conversation..."
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            <MessageCircle size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GroupConversation;