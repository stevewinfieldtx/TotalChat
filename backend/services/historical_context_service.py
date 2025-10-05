# backend/services/historical_context_service.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import wikipedia
import asyncio
from elasticsearch import AsyncElasticsearch

@dataclass
class HistoricalPeriod:
    name: str
    start_year: int
    end_year: int
    key_events: List[Dict]
    cultural_context: Dict[str, Any]
    social_structures: Dict[str, Any]
    language_patterns: Dict[str, Any]
    technological_level: str
    common_knowledge: List[str]
    contemporary_figures: List[str]

@dataclass
class HistoricalContext:
    period: HistoricalPeriod
    character_specific_context: Dict[str, Any]
    contemporary_events: List[Dict]
    relevant_knowledge: List[str]
    anachronisms_to_avoid: List[str]
    appropriate_language: Dict[str, str]

class HistoricalContextService:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.historical_periods = self._load_historical_periods()
        self.context_cache = {}
        self.anachronism_detector = self._initialize_anachronism_detector()
        
    async def get_historical_context(self, character_id: str, 
                                   character_period: str,
                                   current_topic: str = None) -> HistoricalContext:
        """Get comprehensive historical context for a character"""
        
        cache_key = f"{character_id}_{character_period}_{current_topic}"
        
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]
        
        # Get base period context
        period = self.historical_periods.get(character_period)
        if not period:
            period = await self._research_historical_period(character_period)
        
        # Get character-specific context
        character_context = await self._get_character_specific_context(character_id, period)
        
        # Get contemporary events relevant to the character's lifetime
        contemporary_events = await self._get_contemporary_events(
            character_context['birth_year'], 
            character_context['death_year']
        )
        
        # Get topic-specific knowledge
        topic_knowledge = []
        if current_topic:
            topic_knowledge = await self._get_topic_knowledge(
                period, current_topic, character_context
            )
        
        # Identify anachronisms to avoid
        anachronisms = await self._identify_anachronisms(period, current_topic)
        
        # Generate appropriate language guidelines
        language_guidelines = await self._generate_language_guidelines(
            period, character_context
        )
        
        historical_context = HistoricalContext(
            period=period,
            character_specific_context=character_context,
            contemporary_events=contemporary_events,
            relevant_knowledge=topic_knowledge,
            anachronisms_to_avoid=anachronisms,
            appropriate_language=language_guidelines
        )
        
        # Cache for future use
        self.context_cache[cache_key] = historical_context
        
        return historical_context
    
    async def enhance_response_with_historical_context(self, 
                                                     character_id: str,
                                                     base_response: str,
                                                     historical_context: HistoricalContext,
                                                     user_message: str) -> str:
        """Enhance a character's response with historical context"""
        
        # Check for anachronisms in user message
        anachronism_warnings = await self._detect_anachronisms_in_message(
            user_message, historical_context
        )
        
        # Add historical references if appropriate
        enhanced_response = await self._add_historical_references(
            base_response, historical_context, user_message
        )
        
        # Adjust language to be period-appropriate
        period_appropriate_response = await self._make_language_period_appropriate(
            enhanced_response, historical_context
        )
        
        # Add contextual explanations if needed
        if anachronism_warnings:
            period_appropriate_response = await self._add_contextual_explanations(
                period_appropriate_response, anachronism_warnings, historical_context
            )
        
        return period_appropriate_response
    
    async def _research_historical_period(self, period_name: str) -> HistoricalPeriod:
        """Research a historical period using various sources"""
        
        # Search Wikipedia for period overview
        try:
            page = wikipedia.page(period_name)
            period_text = page.content
            
            # Extract key information using AI
            extraction_prompt = f"""
            Analyze this historical period description and extract:
            1. Time period (start and end years)
            2. Key events with dates
            3. Cultural characteristics
            4. Social structures
            5. Language patterns
            6. Technological level
            7. Important figures
            
            Text: {period_text[:5000]}
            
            Return as structured JSON.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.3
            )
            
            period_data = json.loads(response.choices[0].message.content)
            
            return HistoricalPeriod(
                name=period_name,
                start_year=period_data.get('start_year', 0),
                end_year=period_data.get('end_year', 0),
                key_events=period_data.get('key_events', []),
                cultural_context=period_data.get('cultural_context', {}),
                social_structures=period_data.get('social_structures', {}),
                language_patterns=period_data.get('language_patterns', {}),
                technological_level=period_data.get('technological_level', 'unknown'),
                common_knowledge=period_data.get('common_knowledge', []),
                contemporary_figures=period_data.get('contemporary_figures', [])
            )
            
        except wikipedia.exceptions.PageError:
            # Fallback to generic period data
            return self._get_generic_period_data(period_name)
    
    async def _get_character_specific_context(self, character_id: str, 
                                            period: HistoricalPeriod) -> Dict[str, Any]:
        """Get context specific to the character's life and experiences"""
        
        # Load character biography
        character_bio = await self._load_character_biography(character_id)
        
        # Calculate what the character would have known
        character_knowledge = {
            'birth_year': character_bio.get('birth_year', period.start_year),
            'death_year': character_bio.get('death_year', period.end_year),
            'lifetime_events': [],
            'personal_experiences': [],
            'contemporary_knowledge': [],
            'blind_spots': []  # Things they wouldn't have known
        }
        
        # Filter events by character's lifetime
        for event in period.key_events:
            if character_knowledge['birth_year'] <= event['year'] <= character_knowledge['death_year']:
                character_knowledge['lifetime_events'].append(event)
        
        # Determine what technologies/concepts they would have known
        character_knowledge['known_technologies'] = self._filter_by_lifetime(
            period.technological_level, character_knowledge['birth_year']
        )
        
        # Identify anachronistic knowledge (things they couldn't have known)
        character_knowledge['blind_spots'] = self._identify_blind_spots(
            period, character_knowledge['death_year']
        )
        
        return character_knowledge
    
    def _identify_blind_spots(self, period: HistoricalPeriod, death_year: int) -> List[str]:
        """Identify things the character couldn't have known"""
        
        blind_spots = []
        
        # Scientific discoveries after their death
        scientific_discoveries = {
            1543: "heliocentric theory",
            1687: "laws of motion",
            1859: "theory of evolution",
            1905: "theory of relativity",
            1928: "penicillin",
            1953: "DNA structure"
        }
        
        for year, discovery in scientific_discoveries.items():
            if year > death_year:
                blind_spots.append(discovery)
        
        # Technological inventions
        inventions = {
            1440: "printing press",
            1712: "steam engine",
            1876: "telephone",
            1903: "airplane",
            1946: "computer",
            1969: "internet"
        }
        
        for year, invention in inventions.items():
            if year > death_year:
                blind_spots.append(invention)
        
        # Political/social developments
        developments = {
            1776: "American independence",
            1789: "French Revolution",
            1865: "end of American slavery",
            1914: "World War I",
            1920: "women's suffrage in US",
            1945: "United Nations"
        }
        
        for year, development in developments.items():
            if year > death_year:
                blind_spots.append(development)
        
        return blind_spots
    
    async def _detect_anachronisms_in_message(self, user_message: str,
                                            historical_context: HistoricalContext) -> List[Dict]:
        """Detect anachronistic references in user messages"""
        
        anachronisms = []
        
        # Check for modern technology references
        modern_tech_words = ['internet', 'computer', 'phone', 'television', 'car', 'airplane']
        for word in modern_tech_words:
            if word.lower() in user_message.lower():
                anachronisms.append({
                    'type': 'technology',
                    'word': word,
                    'explanation': f"{word} was not invented in {historical_context.period.name}"
                })
        
        # Check for modern concepts
        modern_concepts = ['democracy', 'human rights', 'feminism', 'climate change']
        for concept in modern_concepts:
            if concept.lower() in user_message.lower():
                # Check if this concept existed in the period
                if not await self._concept_existed_in_period(concept, historical_context.period):
                    anachronisms.append({
                        'type': 'concept',
                        'word': concept,
                        'explanation': f"The concept of {concept} as understood today didn't exist"
                    })
        
        # Check for modern figures
        modern_f igures = ['Einstein', 'Newton', 'Darwin', 'Freud']
        for figure in modern_figures:
            if figure.lower() in user_message.lower():
                # Check if this person was alive during the period
                if not await self._person_was_alive(figure, historical_context.period):
                    anachronisms.append({
                        'type': 'person',
                        'word': figure,
                        'explanation': f"{figure} lived after this historical period"
                    })
        
        return anachronisms
    
    async def _add_historical_references(self, response: str,
                                       historical_context: HistoricalContext,
                                       user_message: str) -> str:
        """Add appropriate historical references to the response"""
        
        # Identify opportunities for historical references
        reference_opportunities = await self._identify_reference_opportunities(
            user_message, historical_context
        )
        
        if not reference_opportunities:
            return response
        
        # Generate historical references
        for opportunity in reference_opportunities:
            if opportunity['type'] == 'event':
                # Reference a contemporary event
                relevant_event = await self._find_relevant_event(
                    opportunity['topic'], historical_context
                )
                if relevant_event:
                    response = await self._naturally_insert_event_reference(
                        response, relevant_event, opportunity
                    )
            
            elif opportunity['type'] == 'figure':
                # Reference a contemporary figure
                relevant_figure = await self._find_relevant_figure(
                    opportunity['topic'], historical_context
                )
                if relevant_figure:
                    response = await self._naturally_insert_figure_reference(
                        response, relevant_figure, opportunity
                    )
            
            elif opportunity['type'] == 'custom':
                # Reference period-appropriate customs or practices
                relevant_custom = await self._find_relevant_custom(
                    opportunity['topic'], historical_context
                )
                if relevant_custom:
                    response = await self._naturally_insert_custom_reference(
                        response, relevant_custom, opportunity
                    )
        
        return response
    
    async def _make_language_period_appropriate(self, response: str,
                                              historical_context: HistoricalContext) -> str:
        """Adjust language to be appropriate for the historical period"""
        
        # Get language guidelines for the period
        guidelines = historical_context.appropriate_language
        
        # Replace modern terms with period-appropriate ones
        for modern_term, period_term in guidelines.get('vocabulary', {}).items():
            response = response.replace(modern_term, period_term)
        
        # Adjust sentence structure if needed
        if guidelines.get('formal_structure'):
            response = await self._formalize_sentence_structure(response)
        
        # Add period-appropriate greetings/farewells
        if guidelines.get('greetings'):
            response = await self._add_period_greetings(response, guidelines)
        
        # Remove anachronistic phrases
        for phrase in guidelines.get('avoid_phrases', []):
            response = response.replace(phrase, '')
        
        return response.strip()
    
    async def _add_contextual_explanations(self, response: str,
                                         anachronisms: List[Dict],
                                         historical_context: HistoricalContext) -> str:
        """Add explanations when anachronisms are detected"""
        
        if not anachronisms:
            return response
        
        explanation_prompt = f"""
        The user mentioned some concepts that didn't exist in {historical_context.period.name}.
        Anachronisms detected: {json.dumps(anachronisms)}
        
        Current response: "{response}"
        
        Add a gentle, educational explanation about these anachronisms while staying in character.
        Make it conversational and informative, not condescending.
        
        Example: "Ah, I see you speak of [concept]. In my time, we knew not of such things, though we did have [period-appropriate alternative]..."
        """
        
        enhanced_response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": explanation_prompt}],
            temperature=0.7
        )
        
        return enhanced_response.choices[0].message.content