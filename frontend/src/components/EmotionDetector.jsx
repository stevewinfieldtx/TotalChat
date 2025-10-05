// frontend/src/components/EmotionDetector.jsx
import React, { useState, useEffect } from 'react';
import { Heart, Brain, Zap, AlertCircle } from 'lucide-react';

const EmotionDetector = ({ emotionAnalysis }) => {
  if (!emotionAnalysis) return null;

  const { primary_emotion, intensity, confidence, emotional_shifts } = emotionAnalysis;

  const emotionColors = {
    joy: 'bg-yellow-400',
    sadness: 'bg-blue-400',
    anger: 'bg-red-400',
    fear: 'bg-purple-400',
    surprise: 'bg-orange-400',
    neutral: 'bg-gray-400',
    frustration: 'bg-orange-600',
    excitement: 'bg-pink-400'
  };

  const emotionIcons = {
    joy: '😊',
    sadness: '😢',
    anger: '😠',
    fear: '😨',
    surprise: '😲',
    neutral: '😐',
    frustration: '😤',
    excitement: '🤩'
  };

  return (
    <div className="emotion-detector bg-white rounded-lg p-4 shadow-md">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold flex items-center gap-2">
          <Brain size={20} />
          Emotion Detection
        </h4>
        <span className="text-sm text-gray-500">
          Confidence: {Math.round(confidence * 100)}%
        </span>
      </div>

      <div className="flex items-center gap-4 mb-3">
        <div className="text-4xl">{emotionIcons[primary_emotion] || '😐'}</div>
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <span className="font-medium capitalize">{primary_emotion}</span>
            <span className="text-sm text-gray-600">{Math.round(intensity * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${emotionColors[primary_emotion] || 'bg-gray-400'}`}
              style={{ width: `${intensity * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {emotional_shifts.length > 0 && (
        <div className="emotional-shifts bg-gray-50 rounded p-3">
          <h5 className="font-medium text-sm mb-2 flex items-center gap-1">
            <Zap size={16} />
            Emotional Shifts Detected
          </h5>
          {emotional_shifts.map((shift, index) => (
            <div key={index} className="text-sm text-gray-600">
              Shifted from {shift.from} to {shift.to} 
              ({shift.intensity_change > 0 ? '+' : ''}{Math.round(shift.intensity_change * 100)}%)
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmotionDetector;