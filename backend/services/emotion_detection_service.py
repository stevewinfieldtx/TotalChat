# backend/services/emotion_detection_service.py
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
import numpy as np
from transformers import pipeline

class EmotionType(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    CONTEMPT = "contempt"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    NEUTRAL = "neutral"
    FRUSTRATION = "frustration"
    EXCITEMENT = "excitement"
    CONFUSION = "confusion"
    EMBARRASSMENT = "embarrassment"
    PRIDE = "pride"
    SHAME = "shame"

@dataclass
class EmotionAnalysis:
    primary_emotion: EmotionType
    secondary_emotions: List[Tuple[EmotionType, float]]
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    emotional_shifts: List[Dict]  # Detect changes in emotion
    contextual_factors: Dict[str, any]
    recommended_response_style: str

class CharacterEmotionDetectionService:
    def __init__(self):
        # Initialize emotion analysis models
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        
    async def analyze_user_emotion(self, user_message: str, 
                                 conversation_history: List[Dict],
                                 character_id: str) -> EmotionAnalysis:
        """Comprehensive emotion analysis of user input"""
        
        # Multi-modal emotion detection
        text_emotions = await self._analyze_text_emotions(user_message)
        contextual_emotions = await self._analyze_contextual_emotions(
            user_message, conversation_history
        )
        behavioral_emotions = await self._analyze_behavioral_patterns(
            user_message, conversation_history
        )
        
        # Combine all analyses
        combined_emotion = self._fuse_emotion_signals(
            text_emotions, contextual_emotions, behavioral_emotions
        )
        
        # Detect emotional shifts
        emotional_shifts = self._detect_emotional_shifts(
            conversation_history, combined_emotion
        )
        
        # Generate response recommendations
        response_style = self._recommend_response_style(
            combined_emotion, character_id
        )
        
        return EmotionAnalysis(
            primary_emotion=combined_emotion['primary'],
            secondary_emotions=combined_emotion['secondary'],
            intensity=combined_emotion['intensity'],
            confidence=combined_emotion['confidence'],
            emotional_shifts=emotional_shifts,
            contextual_factors=combined_emotion['context'],
            recommended_response_style=response_style
        )
    
    async def _analyze_text_emotions(self, text: str) -> Dict:
        """Analyze emotions from text content using NLP"""
        
        # Get base emotion predictions
        emotion_scores = self.emotion_classifier(text)[0]
        
        # Analyze linguistic markers
        linguistic_markers = self._extract_linguistic_emotion_markers(text)
        
        # Check for sarcasm/irony
        sarcasm_detected = await self._detect_sarcasm(text)
        
        # Analyze sentence structure and punctuation
        structural_emotions = self._analyze_structural_emotions(text)
        
        return {
            'emotion_scores': emotion_scores,
            'linguistic_markers': linguistic_markers,
            'sarcasm_detected': sarcasm_detected,
            'structural_emotions': structural_emotions,
            'text_complexity': len(text.split()) / 10  # Words per sentence
        }
    
    async def _analyze_contextual_emotions(self, text: str, 
                                         history: List[Dict]) -> Dict:
        """Analyze emotions based on conversation context"""
        
        if not history:
            return {'context_emotions': {}, 'continuity_score': 0}
        
        # Analyze emotional continuity
        recent_emotions = [msg.get('emotion_analysis', {}) for msg in history[-5:]]
        continuity_score = self._calculate_emotional_continuity(text, recent_emotions)
        
        # Check for emotional triggers from previous messages
        emotional_triggers = self._identify_emotional_triggers(text, history)
        
        # Analyze conversational patterns
        pattern_emotions = self._analyze_conversational_patterns(text, history)
        
        return {
            'context_emotions': {
                'continuity_score': continuity_score,
                'triggers': emotional_triggers,
                'patterns': pattern_emotions
            }
        }
    
    def _extract_linguistic_emotion_markers(self, text: str) -> Dict:
        """Extract linguistic markers that indicate emotions"""
        
        # Intensity markers
        intensity_words = ['very', 'extremely', 'incredibly', 'absolutely', 'totally']
        intensity_count = sum(1 for word in intensity_words if word in text.lower())
        
        # Uncertainty markers
        uncertainty_words = ['maybe', 'perhaps', 'might', 'could', 'possibly']
        uncertainty_count = sum(1 for word in uncertainty_words if word in text.lower())
        
        # Emotional vocabulary
        emotional_words = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'joyful'],
            'anger': ['angry', 'furious', 'mad', 'annoyed', 'irritated'],
            'sadness': ['sad', 'disappointed', 'upset', 'depressed', 'melancholy'],
            'fear': ['afraid', 'scared', 'worried', 'anxious', 'terrified'],
            'surprise': ['amazing', 'unbelievable', 'wow', 'incredible', 'shocking']
        }
        
        emotion_word_count = {}
        for emotion, words in emotional_words.items():
            count = sum(1 for word in words if word in text.lower())
            emotion_word_count[emotion] = count
        
        # Exclamation and question patterns
        exclamations = text.count('!') / len(text.split())
        questions = text.count('?') / len(text.split())
        
        return {
            'intensity_markers': intensity_count,
            'uncertainty_markers': uncertainty_count,
            'emotion_vocabulary': emotion_word_count,
            'exclamation_ratio': exclamations,
            'question_ratio': questions,
            'caps_ratio': sum(1 for c in text if c.isupper()) / len(text)
        }
    
    async def _detect_sarcasm(self, text: str) -> float:
        """Detect sarcasm and irony in text"""
        
        sarcasm_indicators = {
            'phrases': ['yeah right', 'oh great', 'just what I needed', 'fantastic'],
            'patterns': ['!', '...', '""'],
            'contradictions': ['love', 'hate', 'amazing', 'terrible']
        }
        
        # Check for sarcasm patterns
        sarcasm_score = 0
        for phrase in sarcasm_indicators['phrases']:
            if phrase in text.lower():
                sarcasm_score += 0.3
        
        # Check for excessive punctuation
        if text.count('!') > 2 or '...' in text:
            sarcasm_score += 0.2
        
        # Use AI model for complex sarcasm detection
        sarcasm_prompt = f"""
        Analyze this text for sarcasm or irony. Consider context, tone, and contradictions.
        Text: "{text}"
        
        Rate sarcasm likelihood 0-1 and explain why.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": sarcasm_prompt}],
            temperature=0.3
        )
        
        ai_score = float(response.choices[0].message.content.split('\n')[0])
        
        return min((sarcasm_score + ai_score) / 2, 1.0)
    
    def _detect_emotional_shifts(self, history: List[Dict], 
                               current_emotion: Dict) -> List[Dict]:
        """Detect changes in emotional state"""
        
        if len(history) < 2:
            return []
        
        shifts = []
        previous_emotion = history[-1].get('emotion_analysis', {})
        
        if previous_emotion:
            # Calculate emotional distance
            prev_primary = previous_emotion.get('primary_emotion', 'neutral')
            curr_primary = current_emotion['primary']
            
            if prev_primary != curr_primary:
                shifts.append({
                    'from': prev_primary,
                    'to': curr_primary,
                    'intensity_change': current_emotion['intensity'] - 
                                      previous_emotion.get('intensity', 0.5),
                    'timestamp': datetime.now().isoformat()
                })
        
        return shifts
    
    def _recommend_response_style(self, emotion_analysis: Dict, 
                                character_id: str) -> str:
        """Recommend how the character should respond based on detected emotions"""
        
        primary_emotion = emotion_analysis['primary']
        intensity = emotion_analysis['intensity']
        
        response_styles = {
            EmotionType.JOY: {
                'style': 'enthusiastic and celebratory',
                'tone': 'warm and engaging',
                'approach': 'share in their happiness',
                'avoid': 'being dismissive or changing subject'
            },
            EmotionType.SADNESS: {
                'style': 'gentle and supportive',
                'tone': 'soft and understanding',
                'approach': 'offer comfort and validation',
                'avoid': 'being overly cheerful or dismissive'
            },
            EmotionType.ANGER: {
                'style': 'calm and understanding',
                'tone': 'measured and respectful',
                'approach': 'acknowledge their feelings',
                'avoid': 'being defensive or argumentative'
            },
            EmotionType.FEAR: {
                'style': 'reassuring and confident',
                'tone': 'steady and comforting',
                'approach': 'provide reassurance and support',
                'avoid': 'dismissing their concerns'
            },
            EmotionType.FRUSTRATION: {
                'style': 'patient and helpful',
                'tone': 'understanding and constructive',
                'approach': 'offer solutions or empathy',
                'avoid': 'being dismissive or overly critical'
            }
        }
        
        return response_styles.get(primary_emotion, {
            'style': 'neutral and observant',
            'tone': 'balanced and thoughtful',
            'approach': 'respond appropriately to context',
            'avoid': 'making assumptions'
        })