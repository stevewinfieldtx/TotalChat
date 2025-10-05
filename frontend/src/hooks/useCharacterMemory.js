// frontend/src/hooks/useCharacterMemory.js
import { useState, useEffect, useCallback } from 'react';
import { memoryAPI } from '../services/api';

export const useCharacterMemory = (characterId, userId) => {
  const [memories, setMemories] = useState([]);
  const [relationship, setRelationship] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [memoryEnabled, setMemoryEnabled] = useState(true);

  // Load memories and relationship data
  const loadMemoryData = useCallback(async () => {
    if (!memoryEnabled) return;

    setIsLoading(true);
    try {
      const [memoriesData, relationshipData] = await Promise.all([
        memoryAPI.getMemories(characterId, userId),
        memoryAPI.getRelationship(characterId, userId)
      ]);
      
      setMemories(memoriesData);
      setRelationship(relationshipData);
    } catch (error) {
      console.error('Error loading memory data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [characterId, userId, memoryEnabled]);

  // Add new memory manually
  const addMemory = useCallback(async (memoryData) => {
    try {
      const newMemory = await memoryAPI.addMemory(characterId, userId, memoryData);
      setMemories(prev => [newMemory, ...prev]);
      return newMemory;
    } catch (error) {
      console.error('Error adding memory:', error);
      throw error;
    }
  }, [characterId, userId]);

  // Update relationship preferences
  const updatePreferences = useCallback(async (preferences) => {
    try {
      await memoryAPI.updatePreferences(characterId, userId, preferences);
      setRelationship(prev => ({ ...prev, user_preferences: preferences }));
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  }, [characterId, userId]);

  // Get relationship phase display
  const getRelationshipPhase = useCallback(() => {
    if (!relationship) return 'stranger';
    
    const phase = relationship.relationship_phase;
    const scores = {
      stranger: { emoji: '🤝', description: 'Getting to know each other' },
      acquaintance: { emoji: '🙂', description: 'Building familiarity' },
      friend: { emoji: '😊', description: 'Developing friendship' },
      close_friend: { emoji: '💛', description: 'Strong connection' },
      intimate: { emoji: '💖', description: 'Deep bond' }
    };
    
    return scores[phase] || scores.stranger;
  }, [relationship]);

  // Calculate relationship progress
  const getRelationshipProgress = useCallback(() => {
    if (!relationship) return 0;
    
    const interactions = relationship.shared_experiences;
    const maxInteractions = 100;
    return Math.min((interactions / maxInteractions) * 100, 100);
  }, [relationship]);

  useEffect(() => {
    loadMemoryData();
    
    // Refresh memory data periodically
    const interval = setInterval(() => {
      loadMemoryData();
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [loadMemoryData]);

  return {
    memories,
    relationship,
    isLoading,
    memoryEnabled,
    setMemoryEnabled,
    addMemory,
    updatePreferences,
    getRelationshipPhase,
    getRelationshipProgress,
    refreshMemory: loadMemoryData
  };
};