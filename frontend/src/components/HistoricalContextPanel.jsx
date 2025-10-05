// frontend/src/components/HistoricalContextPanel.jsx
import React, { useState, useEffect } from 'react';
import { Clock, Book, Users, Globe, AlertTriangle } from 'lucide-react';

const HistoricalContextPanel = ({ character, currentTopic }) => {
  const [historicalContext, setHistoricalContext] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadHistoricalContext = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `/api/characters/${character.id}/historical-context?topic=${currentTopic || ''}`
        );
        const data = await response.json();
        setHistoricalContext(data);
      } catch (error) {
        console.error('Error loading historical context:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadHistoricalContext();
  }, [character.id, currentTopic]);

  if (isLoading) {
    return (
      <div className="historical-context-panel bg-white rounded-lg p-6 shadow-md">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (!historicalContext) {
    return (
      <div className="historical-context-panel bg-white rounded-lg p-6 shadow-md text-center text-gray-500">
        <Clock size={48} className="mx-auto mb-4 opacity-50" />
        <p>Historical context unavailable</p>
      </div>
    );
  }

  const { period, character_specific_context, anachronisms_to_avoid } = historicalContext;

  return (
    <div className="historical-context-panel bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 p-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold flex items-center gap-2">
              <Clock size={20} />
              Historical Context: {period.name}
            </h3>
            <p className="text-sm opacity-90">
              {period.start_year} - {period.end_year}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">
              {character.birth_year || '?'} - {character.death_year || '?'}
            </div>
            <p className="text-xs opacity-90">Character's Lifetime</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        {['overview', 'events', 'culture', 'anachronisms'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium capitalize flex items-center gap-1 ${
              activeTab === tab 
                ? 'border-b-2 border-orange-500 text-orange-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'overview' && <Globe size={16} />}
            {tab === 'events' && <Book size={16} />}
            {tab === 'culture' && <Users size={16} />}
            {tab === 'anachronisms' && <AlertTriangle size={16} />}
            {tab}
          </button>
        ))}
      </div>

      <div className="p-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Technological Level</h4>
              <p className="text-sm text-gray-600">{period.technological_level}</p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Social Structures</h4>
              <div className="text-sm text-gray-600">
                {Object.entries(period.social_structures).map(([key, value]) => (
                  <div key={key} className="mb-1">
                    <span className="font-medium capitalize">{key}:</span> {value}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Character's Perspective</h4>
              <div className="bg-amber-50 rounded-lg p-3 text-sm">
                <p className="mb-2">
                  This character would have known about:
                </p>
                <ul className="list-disc list-inside space-y-1">
                  {character_specific_context.lifetime_events.slice(0, 3).map((event, index) => (
                    <li key={index}>{event.year}: {event.title}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {period.key_events.slice(0, 10).map((event, index) => (
              <div key={index} className="border-l-4 border-orange-400 pl-3">
                <div className="font-medium text-sm">{event.title}</div>
                <div className="text-xs text-gray-500">{event.year}</div>
                <div className="text-xs text-gray-600 mt-1">{event.description}</div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'culture' && (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Cultural Context</h4>
              <div className="text-sm text-gray-600 space-y-2">
                {Object.entries(period.cultural_context).map(([key, value]) => (
                  <div key={key}>
                    <span className="font-medium capitalize">{key.replace('_', ' ')}:</span> {value}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Language Patterns</h4>
              <div className="bg-gray-50 rounded-lg p-3 text-sm">
                <div className="space-y-2">
                  <div>
                    <span className="font-medium">Formality Level:</span> {period.language_patterns.formality_level}
                  </div>
                  <div>
                    <span className="font-medium">Common Phrases:</span>
                    <ul className="list-disc list-inside mt-1">
                      {period.language_patterns.common_phrases?.slice(0, 3).map((phrase, index) => (
                        <li key={index}>{phrase}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'anachronisms' && (
          <div className="space-y-3">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <h4 className="font-semibold mb-2 text-yellow-800">Things to Avoid</h4>
              <p className="text-sm text-yellow-700 mb-3">
                These concepts didn't exist in {character.name}'s time:
              </p>
              <div className="space-y-2">
                {anachronisms_to_avoid.slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <AlertTriangle size={16} className="text-yellow-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-sm">{item.word}</div>
                      <div className="text-xs text-yellow-600">{item.explanation}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <h4 className="font-semibold mb-2 text-blue-800">Tips</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Use period-appropriate language and concepts</li>
                <li>• Ask about their contemporary world and experiences</li>
                <li>• Avoid modern references they wouldn't understand</li>
                <li>• Be curious about their historical perspective</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricalContextPanel;