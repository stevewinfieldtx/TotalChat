# backend/services/nsfw_content_service.py
import asyncio
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
import openai
from better_profanity import profanity
import requests
import base64
from io import BytesIO
from PIL import Image

class NSFWContentService:
    def __init__(self):
        # Initialize content detection APIs
        self.openai_client = openai.AsyncClient()
        self.profanity_filter = profanity
        self.word_blacklist = self._load_blacklist_words()
        
        # External API configurations
        self.api_configs = {
            'sightengine': {
                'api_key': os.getenv('SIGHTENGINE_API_KEY'),
                'api_user': os.getenv('SIGHTENGINE_API_USER'),
                'base_url': 'https://api.sightengine.com/1.0/'
            },
            'clarifai': {
                'api_key': os.getenv('CLARIFAI_API_KEY'),
                'base_url': 'https://api.clarifai.com/v2/'
            },
            'google_vision': {
                'api_key': os.getenv('GOOGLE_VISION_API_KEY'),
                'base_url': 'https://vision.googleapis.com/v1/'
            }
        }
        
    async def analyze_content(self, content: str, content_type: NSFWContentType,
                            user_content_policy: ContentPolicy) -> ContentAnalysis:
        """Comprehensive content analysis for NSFW detection"""
        
        analysis_tasks = []
        
        if content_type == NSFWContentType.TEXT:
            analysis_tasks.append(self._analyze_text_content(content))
            analysis_tasks.append(self._analyze_text_sentiment(content))
            analysis_tasks.append(self._check_profanity(content))
            
        elif content_type == NSFWContentType.IMAGE:
            analysis_tasks.append(self._analyze_image_content(content))
            analysis_tasks.append(self._detect_explicit_images(content))
            
        elif content_type == NSFWContentType.AUDIO:
            analysis_tasks.append(self._analyze_audio_content(content))
            
        elif content_type == NSFWContentType.VIDEO:
            analysis_tasks.append(self._analyze_video_content(content))
        
        # Run all analyses concurrently
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Combine results
        combined_analysis = self._combine_analysis_results(results, content_type)
        
        # Apply user policy filters
        final_analysis = self._apply_policy_filters(combined_analysis, user_content_policy)
        
        return final_analysis
    
    async def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for NSFW material using AI"""
        
        prompt = f"""
        Analyze the following text for inappropriate or NSFW content. 
        Consider: sexual content, violence, hate speech, drug references, and other adult themes.
        
        Text: "{text}"
        
        Return JSON with:
        - is_nsfw: boolean
        - confidence: float (0-1)
        - categories: list of inappropriate categories found
        - severity: int (1-10)
        - explanation: brief explanation of why it's flagged
        - flagged_phrases: specific problematic phrases
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'text_analysis': result,
                'method': 'ai_analysis'
            }
        except Exception as e:
            return {
                'text_analysis': {
                    'is_nsfw': False,
                    'confidence': 0,
                    'categories': [],
                    'severity': 0,
                    'explanation': 'Analysis failed',
                    'flagged_phrases': []
                },
                'method': 'ai_analysis',
                'error': str(e)
            }
    
    async def _analyze_image_content(self, image_data: str) -> Dict[str, Any]:
        """Analyze images for NSFW content using multiple APIs"""
        
        results = {}
        
        # Sightengine analysis
        if self.api_configs['sightengine']['api_key']:
            sightengine_result = await self._sightengine_nsfw_detection(image_data)
            results['sightengine'] = sightengine_result
        
        # Google Vision SafeSearch
        if self.api_configs['google_vision']['api_key']:
            google_result = await self._google_vision_safe_search(image_data)
            results['google_vision'] = google_result
        
        # Clarifai analysis
        if self.api_configs['clarifai']['api_key']:
            clarifai_result = await self._clarifai_explicit_content_detection(image_data)
            results['clarifai'] = clarifai_result
        
        return {
            'image_analysis': results,
            'consensus': self._calculate_image_consensus(results)
        }
    
    async def _sightengine_nsfw_detection(self, image_data: str) -> Dict[str, Any]:
        """Use Sightengine API for NSFW detection"""
        
        # Convert base64 to URL or process directly
        if image_data.startswith('data:image'):
            # Handle base64 image data
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Save temporarily or process directly
            files = {'media': ('image.jpg', image_bytes, 'image/jpeg')}
            
            params = {
                'models': 'nudity,wad,offensive',
                'api_user': self.api_configs['sightengine']['api_user'],
                'api_secret': self.api_configs['sightengine']['api_key']
            }
            
            try:
                response = requests.post(
                    self.api_configs['sightengine']['base_url'] + 'check.json',
                    files=files,
                    params=params
                )
                result = response.json()
                
                return {
                    'nudity': result.get('nudity', {}),
                    'weapon_alcohol_drugs': result.get('weapon_alcohol_drugs', {}),
                    'offensive': result.get('offensive', {}),
                    'confidence': result.get('confidence', 0)
                }
            except Exception as e:
                return {'error': str(e)}
        
        return {'error': 'Invalid image format'}
    
    async def _google_vision_safe_search(self, image_data: str) -> Dict[str, Any]:
        """Use Google Vision SafeSearch API"""
        
        # Prepare request
        request_body = {
            'requests': [{
                'image': {
                    'content': image_data.split(',')[1] if image_data.startswith('data:image') else image_data
                },
                'features': [{
                    'type': 'SAFE_SEARCH_DETECTION',
                    'maxResults': 10
                }]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.api_configs['google_vision']['base_url']}images:annotate",
                params={'key': self.api_configs['google_vision']['api_key']},
                json=request_body
            )
            result = response.json()
            
            if 'responses' in result and result['responses']:
                safe_search = result['responses'][0].get('safeSearchAnnotation', {})
                return {
                    'adult': safe_search.get('adult', 'UNKNOWN'),
                    'spoof': safe_search.get('spoof', 'UNKNOWN'),
                    'medical': safe_search.get('medical', 'UNKNOWN'),
                    'violence': safe_search.get('violence', 'UNKNOWN'),
                    'racy': safe_search.get('racy', 'UNKNOWN')
                }
        except Exception as e:
            return {'error': str(e)}
        
        return {}
    
    def _combine_analysis_results(self, results: List[Dict], 
                                content_type: NSFWContentType) -> ContentAnalysis:
        """Combine results from multiple analysis methods"""
        
        combined_result = {
            'content_type': content_type,
            'is_nsfw': False,
            'confidence_score': 0.0,
            'categories': [],
            'severity_level': 0,
            'flagged_words': [],
            'suggested_action': 'allow',
            'explanation': ''
        }
        
        if content_type == NSFWContentType.TEXT:
            # Combine text analysis results
            text_results = [r for r in results if isinstance(r, dict) and 'text_analysis' in r]
            if text_results:
                main_result = text_results[0]['text_analysis']
                combined_result.update({
                    'is_nsfw': main_result.get('is_nsfw', False),
                    'confidence_score': main_result.get('confidence', 0),
                    'categories': main_result.get('categories', []),
                    'severity_level': main_result.get('severity', 0),
                    'flagged_words': main_result.get('flagged_phrases', []),
                    'explanation': main_result.get('explanation', '')
                })
        
        elif content_type == NSFWContentType.IMAGE:
            # Combine image analysis results
            image_results = [r for r in results if isinstance(r, dict) and 'image_analysis' in r]
            if image_results:
                consensus = image_results[0].get('consensus', {})
                combined_result.update({
                    'is_nsfw': consensus.get('is_nsfw', False),
                    'confidence_score': consensus.get('confidence', 0),
                    'categories': consensus.get('categories', []),
                    'severity_level': consensus.get('severity', 0),
                    'explanation': consensus.get('explanation', '')
                })
        
        # Determine suggested action based on severity
        if combined_result['severity_level'] >= 8:
            combined_result['suggested_action'] = 'block'
        elif combined_result['severity_level'] >= 5:
            combined_result['suggested_action'] = 'warn'
        elif combined_result['is_nsfw']:
            combined_result['suggested_action'] = 'review'
        
        return ContentAnalysis(**combined_result)
    
    def _apply_policy_filters(self, analysis: ContentAnalysis,
                            user_policy: ContentPolicy) -> ContentAnalysis:
        """Apply user's content policy to the analysis"""
        
        # Check against user's content level
        if user_policy.content_level == ContentLevel.SAFE and analysis.is_nsfw:
            analysis.suggested_action = 'block'
            analysis.explanation += ' [Blocked by user content policy]'
        
        elif user_policy.content_level == ContentLevel.SUGGESTIVE and analysis.severity_level > 3:
            analysis.suggested_action = 'block'
            analysis.explanation += ' [Blocked by user content policy]'
        
        elif user_policy.content_level == ContentLevel.MATURE and analysis.severity_level > 7:
            analysis.suggested_action = 'block'
            analysis.explanation += ' [Blocked by user content policy]'
        
        # Check custom filters
        for custom_filter in user_policy.custom_filters:
            if custom_filter.lower() in analysis.explanation.lower():
                analysis.suggested_action = 'block'
                analysis.explanation += f' [Blocked by custom filter: {custom_filter}]'
                break
        
        return analysis