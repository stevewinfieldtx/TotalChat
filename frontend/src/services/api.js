// frontend/src/services/api.js
// Get backend URL - same origin in prod (Railway), localhost in dev
const getBackendUrl = () => {
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl) return envUrl.replace(/\/?$/, '');
  if (import.meta.env.PROD) return window.location.origin;
  return 'http://localhost:8000';
};

const API_BASE_URL = getBackendUrl();

// ============================================
// CHAT API
// ============================================
export const chatAPI = {
  // Send message to characters
  sendMessage: async (characterIds, message, conversationHistory = []) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_ids: characterIds,
          message: message,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send message');
      }

      return await response.json();
    } catch (error) {
      console.error('Chat API Error:', error);
      throw error;
    }
  },

  // Get character response (streaming)
  getCharacterResponse: async (characterId, message, educationLevel = 'middle_school_6to8') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/character/${characterId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          education_level: educationLevel,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get character response');
      }

      return await response.json();
    } catch (error) {
      console.error('Character Response Error:', error);
      throw error;
    }
  },
};

// ============================================
// CHARACTER API
// ============================================
export const characterAPI = {
  // Load character data
  loadCharacter: async (characterId, category = 'Education') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/characters/${category}/${characterId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load character');
      }

      return await response.json();
    } catch (error) {
      console.error('Character Load Error:', error);
      throw error;
    }
  },

  // Get character images
  getCharacterImages: async (characterId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/characters/${characterId}/images`);
      
      if (!response.ok) {
        throw new Error('Failed to get character images');
      }

      return await response.json();
    } catch (error) {
      console.error('Character Images Error:', error);
      // Return placeholder on error
      return {
        images: [
          `https://api.dicebear.com/7.x/avataaars/svg?seed=${characterId}`,
          `https://api.dicebear.com/7.x/avataaars/svg?seed=${characterId}2`,
          `https://api.dicebear.com/7.x/avataaars/svg?seed=${characterId}3`,
        ]
      };
    }
  },
};

// ============================================
// MEMORY API
// ============================================
export const memoryAPI = {
  // Get character memories
  getMemories: async (characterId, userId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/memory/${characterId}/${userId}/memories`
      );
      
      if (!response.ok) {
        throw new Error('Failed to get memories');
      }

      return await response.json();
    } catch (error) {
      console.error('Memory API Error:', error);
      return [];
    }
  },

  // Get relationship data
  getRelationship: async (characterId, userId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/memory/${characterId}/${userId}/relationship`
      );
      
      if (!response.ok) {
        throw new Error('Failed to get relationship');
      }

      return await response.json();
    } catch (error) {
      console.error('Relationship API Error:', error);
      return null;
    }
  },

  // Add new memory
  addMemory: async (characterId, userId, memoryData) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/memory/${characterId}/${userId}/add`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(memoryData),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to add memory');
      }

      return await response.json();
    } catch (error) {
      console.error('Add Memory Error:', error);
      throw error;
    }
  },

  // Update user preferences
  updatePreferences: async (characterId, userId, preferences) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/memory/${characterId}/${userId}/preferences`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(preferences),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update preferences');
      }

      return await response.json();
    } catch (error) {
      console.error('Update Preferences Error:', error);
      throw error;
    }
  },
};

// ============================================
// VOICE API
// ============================================
export const voiceAPI = {
  // Text to speech
  textToSpeech: async (text, voiceId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice_id: voiceId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to synthesize speech');
      }

      // Return audio blob
      return await response.blob();
    } catch (error) {
      console.error('Voice API Error:', error);
      throw error;
    }
  },
};

// ============================================
// UTILITY FUNCTIONS
// ============================================
export const apiUtils = {
  // Check backend health
  checkHealth: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  },

  // Get API configuration
  getConfig: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config`);
      if (!response.ok) throw new Error('Failed to get config');
      return await response.json();
    } catch (error) {
      console.error('Config API Error:', error);
      return null;
    }
  },
};

export default {
  chat: chatAPI,
  character: characterAPI,
  memory: memoryAPI,
  voice: voiceAPI,
  utils: apiUtils,
};