import { useState, useCallback, useRef } from 'react';
import api from '../services/api';

export const useChat = (characterId) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const sendMessage = useCallback(async (content, options = {}) => {
    if (!content?.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      const response = await api.sendMessage({
        characterId,
        message: content.trim(),
        history: messages,
        ...options
      }, abortControllerRef.current.signal);

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        emotion: response.emotion,
        imageUrl: response.imageUrl,
        audioUrl: response.audioUrl,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      return assistantMessage;

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Request cancelled');
        return;
      }
      
      const errorMessage = err.message || 'Failed to send message';
      setError(errorMessage);
      
      // Add error message to chat
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}`,
        isError: true,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
      
      throw err;
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [characterId, messages]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    cancelRequest
  };
};

export default useChat;