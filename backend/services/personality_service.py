# backend/services/personality_service.py
from typing import Dict, List, Any
from datetime import datetime
import json

class PersonalityEvolutionService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.base_personalities = {}
        
    async def evolve_character_personality(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """Evolve character personality based on relationship history"""
        
        # Get relationship data
        relationship = await self._get_relationship(character_id, user_id)
        
        # Get relevant memories
        memories = await self.memory_service.retrieve_relevant_memories(
            character_id, user_id, "personality evolution", limit=50
        )
        
        # Analyze patterns in memories
        personality_changes = await self._analyze_personality_changes(memories)
        
        # Generate evolved personality traits
        evolved_traits = await self._generate_evolved_personality(
            character_id, relationship, personality_changes
        )
        
        return evolved_traits
    
    async def _analyze_personality_changes(self, memories: List[Memory]) -> Dict[str, Any]:
        """Analyze how interactions have affected character personality"""
        
        changes = {
            'confidence_boost': 0,
            'empathy_increase': 0,
            'humor_development': 0,
            'trust_issues': 0,
            'emotional_openness': 0,
            'shared_interests': [],
            'communication_style': 'neutral'
        }
        
        for memory in memories:
            # Analyze emotional content
            if memory.memory_type == MemoryType.EMOTIONAL:
                if memory.emotional_weight > 1.5:
                    if 'positive' in memory.tags:
                        changes['confidence_boost'] += 0.1
                        changes['emotional_openness'] += 0.05
                    elif 'negative' in memory.tags:
                        changes['trust_issues'] += 0.05
            
            # Track shared interests
            if memory.memory_type == MemoryType.SEMANTIC:
                if 'interests' in memory.tags:
                    changes['shared_interests'].extend(memory.tags)
            
            # Analyze communication patterns
            if 'humor' in memory.tags:
                changes['humor_development'] += 0.02
            if 'deep_conversation' in memory.tags:
                changes['empathy_increase'] += 0.03
        
        return changes
    
    async def _generate_evolved_personality(self, character_id: str, relationship: Dict, 
                                          changes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new personality traits based on relationship development"""
        
        prompt = f"""
        Given a character's base personality and their relationship development with a user,
        generate evolved personality traits that reflect their growth and adaptation.
        
        Relationship Phase: {relationship['relationship_phase']}
        Familiarity Score: {relationship['familiarity_score']}
        Trust Score: {relationship['trust_score']}
        Affection Score: {relationship['affection_score']}
        
        Personality Changes Detected:
        {json.dumps(changes, indent=2)}
        
        Generate updated personality traits that show how the character has evolved:
        - Speaking style adaptations
        - New interests or topics they might bring up
        - Changes in emotional expression
        - Trust-related behaviors
        - Inside jokes or shared references
        
        Return as JSON with clear trait categories.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)