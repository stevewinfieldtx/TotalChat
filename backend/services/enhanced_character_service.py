# backend/services/enhanced_character_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class EnhancedCharacterService:
    def __init__(self, memory_service: MemoryService, personality_service: PersonalityEvolutionService):
        self.memory_service = memory_service
        self.personality_service = personality_service
        
    async def generate_character_response(self, character_id: str, user_id: str, 
                                        message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Generate response using memory and relationship context"""
        
        # Retrieve relevant memories
        relevant_memories = await self.memory_service.retrieve_relevant_memories(
            character_id, user_id, message, limit=10
        )
        
        # Get relationship data
        relationship = await self._get_relationship_data(character_id, user_id)
        
        # Get evolved personality
        evolved_personality = await self.personality_service.evolve_character_personality(
            character_id, user_id
        )
        
        # Extract user preferences and patterns
        user_preferences = await self._extract_user_preferences(relevant_memories)
        
        # Generate contextual response
        response_data = await self._create_contextual_response(
            character_id, message, relevant_memories, relationship, 
            evolved_personality, user_preferences, conversation_history
        )
        
        # Store new memories from this interaction
        await self._store_interaction_memories(character_id, user_id, message, response_data)
        
        return response_data
    
    async def _create_contextual_response(self, character_id: str, user_message: str,
                                        memories: List[Memory], relationship: Dict,
                                        personality: Dict, preferences: Dict,
                                        history: List[Dict]) -> Dict[str, Any]:
        """Create response with full context awareness"""
        
        # Format memory context
        memory_context = self._format_memory_context(memories)
        
        # Format relationship context
        relationship_context = self._format_relationship_context(relationship)
        
        # Format personality context
        personality_context = self._format_personality_context(personality)
        
        # Create comprehensive prompt
        prompt = f"""
        You are roleplaying as a character with the following context:
        
        {personality_context}
        
        Relationship with user:
        {relationship_context}
        
        Relevant memories:
        {memory_context}
        
        User preferences:
        {json.dumps(preferences, indent=2)}
        
        Recent conversation history:
        {json.dumps(history[-5:], indent=2)}
        
        User's latest message: "{user_message}"
        
        Generate a response that:
        1. Shows recognition of shared history and inside jokes
        2. Demonstrates evolved personality traits
        3. References relevant past conversations naturally
        4. Shows appropriate emotional depth based on relationship
        5. Uses personalized communication style
        6. Asks follow-up questions about remembered topics
        
        Make the response feel natural and conversational, not robotic or overly referential.
        """
        
        # Generate response using OpenRouter
        response = await self._call_openrouter(prompt, character_id)
        
        # Extract emotional tone for memory tagging
        emotional_analysis = await self._analyze_emotional_tone(response)
        
        return {
            'content': response,
            'emotional_tone': emotional_analysis,
            'referenced_memories': [m.id for m in memories[:3]],  # Track which memories influenced response
            'relationship_update': self._calculate_relationship_update(response, relationship)
        }
    
    def _format_memory_context(self, memories: List[Memory]) -> str:
        """Format memories into contextual narrative"""
        
        if not memories:
            return "No specific memories to reference."
        
        context_parts = []
        
        # Group memories by type
        by_type = {}
        for memory in memories:
            if memory.memory_type not in by_type:
                by_type[memory.memory_type] = []
            by_type[memory.memory_type].append(memory)
        
        # Create contextual descriptions
        if MemoryType.EPISODIC in by_type:
            recent_events = by_type[MemoryType.EPISODIC][:3]
            context_parts.append(f"Recent events to remember: " + 
                               ", ".join([m.content for m in recent_events]))
        
        if MemoryType.SEMANTIC in by_type:
            facts = by_type[MemoryType.SEMANTIC][:5]
            context_parts.append(f"What I know about you: " + 
                               ", ".join([m.content for m in facts]))
        
        if MemoryType.EMOTIONAL in by_type:
            emotions = by_type[MemoryType.EMOTIONAL][:3]
            context_parts.append(f"Emotional moments we've shared: " + 
                               ", ".join([m.content for m in emotions]))
        
        return "\n".join(context_parts)
    
    def _format_relationship_context(self, relationship: Dict) -> str:
        """Format relationship data into context"""
        
        phase = relationship['relationship_phase']
        familiarity = relationship['familiarity_score']
        trust = relationship['trust_score']
        affection = relationship['affection_score']
        
        context = f"Our relationship is at the '{phase}' stage. "
        
        if familiarity > 0.7:
            context += "We know each other very well. "
        elif familiarity > 0.4:
            context += "We're getting to know each other. "
        else:
            context += "We're still learning about each other. "
        
        if trust > 0.8:
            context += "There's deep trust between us. "
        elif trust > 0.6:
            context += "We trust each other. "
        
        if affection > 0.7:
            context += "I care about you deeply. "
        elif affection > 0.5:
            context += "I enjoy our conversations. "
        
        context += f"We've shared {relationship['shared_experiences']} experiences together."
        
        return context