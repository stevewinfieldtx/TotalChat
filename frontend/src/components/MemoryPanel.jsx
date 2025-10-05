// frontend/src/components/MemoryPanel.jsx
import React, { useState } from 'react';
import { useCharacterMemory } from '../hooks/useCharacterMemory';
import { Brain, Heart, Users, Clock, TrendingUp } from 'lucide-react';

const MemoryPanel = ({ characterId, userId }) => {
  const {
    memories,
    relationship,
    isLoading,
    memoryEnabled,
    setMemoryEnabled,
    getRelationshipPhase,
    getRelationshipProgress
  } = useCharacterMemory(characterId, userId);

  const [activeTab, setActiveTab] = useState('overview');

  const phaseInfo = getRelationshipPhase();
  const progress = getRelationshipProgress();

  const MemoryCard = ({ memory }) => {
    const typeIcons = {
      episodic: '📝',
      semantic: '🧠',
      emotional: '💭',
      relational: '🔗',
      contextual: '🌍'
    };

    const priorityColors = {
      3: 'border-red-300 bg-red-50',
      2: 'border-yellow-300 bg-yellow-50',
      1: 'border-green-300 bg-green-50'
    };

    return (
      <div className={`memory-card ${priorityColors[memory.priority]} mb-3 p-3 rounded-lg border`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">{typeIcons[memory.memory_type]}</span>
            <div>
              <p className="text-sm font-medium text-gray-800">{memory.content}</p>
              <div className="flex gap-2 mt-1">
                {memory.tags.map(tag => (
                  <span key={tag} className="text-xs bg-gray-200 px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <span className="text-xs text-gray-500">
            {new Date(memory.timestamp).toLocaleDateString()}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="memory-panel bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Brain size={24} />
          Character Memory & Relationship
        </h3>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={memoryEnabled}
            onChange={(e) => setMemoryEnabled(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Enable Memory</span>
        </label>
      </div>

      {!memoryEnabled ? (
        <div className="text-center py-8 text-gray-500">
          <Brain size={48} className="mx-auto mb-4 opacity-50" />
          <p>Memory system is disabled</p>
        </div>
      ) : isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      ) : (
        <>
          {/* Relationship Overview */}
          <div className="relationship-overview mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{phaseInfo.emoji}</span>
                <div>
                  <h4 className="font-semibold text-lg">Relationship Status</h4>
                  <p className="text-sm text-gray-600">{phaseInfo.description}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(progress)}%
                </div>
                <p className="text-xs text-gray-500">Connection Level</p>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>

            {/* Relationship Stats */}
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Heart size={16} className="text-red-500" />
                  <span className="text-sm font-semibold">
                    {Math.round((relationship?.affection_score || 0.5) * 100)}%
                  </span>
                </div>
                <p className="text-xs text-gray-500">Affection</p>
              </div>
              <div>
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Users size={16} className="text-blue-500" />
                  <span className="text-sm font-semibold">
                    {Math.round((relationship?.trust_score || 0.5) * 100)}%
                  </span>
                </div>
                <p className="text-xs text-gray-500">Trust</p>
              </div>
              <div>
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp size={16} className="text-green-500" />
                  <span className="text-sm font-semibold">
                    {relationship?.shared_experiences || 0}
                  </span>
                </div>
                <p className="text-xs text-gray-500">Shared Moments</p>
              </div>
              <div>
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Clock size={16} className="text-purple-500" />
                  <span className="text-sm font-semibold">
                    {relationship?.interaction_frequency?.toFixed(1) || '0.0'}
                  </span>
                </div>
                <p className="text-xs text-gray-500">Daily Chats</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b mb-4">
            {['overview', 'memories', 'insights'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-medium capitalize ${
                  activeTab === tab 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium mb-2">Recent Topics</h5>
                  <div className="flex flex-wrap gap-2">
                    {relationship?.conversation_topics?.slice(0, 5).map(topic => (
                      <span key={topic} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {topic}
                      </span>
                    )) || <span className="text-sm text-gray-500">No topics yet</span>}
                  </div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium mb-2">Emotional Connections</h5>
                  <div className="flex flex-wrap gap-2">
                    {relationship?.emotional_connections?.slice(0, 5).map(conn => (
                      <span key={conn} className="text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded">
                        {conn}
                      </span>
                    )) || <span className="text-sm text-gray-500">Building connections</span>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'memories' && (
            <div className="max-h-96 overflow-y-auto">
              {memories.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No memories yet. Start chatting!</p>
              ) : (
                memories.map(memory => (
                  <MemoryCard key={memory.id} memory={memory} />
                ))
              )}
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-4">
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <h5 className="font-medium mb-2">💡 Relationship Insights</h5>
                <ul className="text-sm space-y-1">
                  <li>• Your connection grows stronger with each conversation</li>
                  <li>• Shared experiences create lasting bonds</li>
                  <li>• Emotional moments are remembered most vividly</li>
                  <li>• Trust builds through consistent, meaningful interactions</li>
                </ul>
              </div>
              
              {progress > 50 && (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <h5 className="font-medium mb-2">🌟 Milestone Achieved!</h5>
                  <p className="text-sm">
                    You've built a strong connection with this character. 
                    They now remember your preferences and shared experiences deeply.
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MemoryPanel;