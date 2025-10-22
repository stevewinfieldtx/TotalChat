import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// Get backend URL - same origin in prod (Railway), localhost in dev
const getBackendUrl = () => {
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl) return envUrl.replace(/\/?$/, '');
  if (import.meta.env.PROD) return window.location.origin;
  return 'http://localhost:8000';
};

// WebSocket chat hook that talks to the FastAPI backend
export const useChat = (characters = []) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState({});
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const clientIdRef = useRef(`${Date.now()}_${Math.floor(Math.random() * 1e6)}`);
  const queueRef = useRef([]); // messages waiting for WS OPEN

  const backendHttp = getBackendUrl();
  const wsBase = backendHttp.startsWith('https')
    ? backendHttp.replace('https', 'wss')
    : backendHttp.replace('http', 'ws');

  // Derive current speaking character (last assistant)
  const currentSpeaker = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      const msg = messages[i];
      if (msg.role !== 'user' && msg.characterId) {
        return characters.find(c => c.id === msg.characterId) || null;
      }
    }
    return characters[0] || null;
  }, [messages, characters]);

  // Open WebSocket when characters are available
  useEffect(() => {
    if (!characters || characters.length === 0) return;

    const url = `${wsBase}/ws/${clientIdRef.current}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // flush any queued messages
      try {
        const q = queueRef.current;
        while (q.length) {
          const payload = q.shift();
          ws.send(JSON.stringify(payload));
        }
      } catch {}
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'character_response') {
          const assistantMessage = {
            id: Date.now(),
            role: 'assistant',
            characterId: data.characterId,
            content: data.content,
            timestamp: data.timestamp || new Date().toISOString(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setIsTyping(prev => ({ ...prev, [data.characterId]: false }));
        }
        // Other message types: voice_data, avatar_prompt, error
      } catch (e) {
        // ignore malformed frames
      }
    };

    ws.onerror = () => {
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      try { ws.close(); } catch {}
      wsRef.current = null;
    };
  }, [wsBase, characters]);

  const sendMessage = useCallback((content) => {
    const text = (content || '').trim();
    if (!text) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    // optimistic typing indicators
    const typingState = {};
    characters.forEach(c => { typingState[c.id] = true; });
    setIsTyping(typingState);

    const ws = wsRef.current;
    const payload = {
      message: text,
      characters: characters.map(c => ({
        id: c.id,
        name: c.name,
        title: c.title,
        images: c.images,
        category: c.category,
        model: c.model,
      })),
      conversation_history: messages.map(m => ({
        role: m.role,
        characterId: m.characterId,
        content: m.content,
        timestamp: m.timestamp,
      })),
    };

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      // Queue and let onopen flush
      queueRef.current.push(payload);
      // Stop typing indicator after short delay if connection still not open
      setTimeout(() => setIsTyping({}), 600);
      return;
    }

    try {
      ws.send(JSON.stringify(payload));
    } catch (e) {
      setTimeout(() => setIsTyping({}), 300);
    }
  }, [characters, messages]);

  return { messages, sendMessage, isTyping, currentSpeaker, connected };
};

export default useChat;