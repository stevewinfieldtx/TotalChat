# backend/services/group_conversation_service.py
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

@dataclass
class ConversationTurn:
    speaker_id: str
    content: str
    timestamp: datetime
    addressed_to: List[str] = None  # Who this message is directed at
    references: List[str] = None    # What/who is being referenced
    emotional_tone: Dict = None
    interruption: bool = False

@dataclass
class GroupConversationState:
    participants: List[str]
    conversation_history: List[ConversationTurn]
    current_speaker: str
    speaking_order: List[str]
    conversation_topic: str
    group_dynamics: Dict[str, Any]
    interpersonal_relationships: Dict[str, Dict]  # Character-to-character relationships

class GroupConversationService:
    def __init__(self, character_services: Dict, memory_service: MemoryService):
        self.character_services = character_services
        self.memory_service = memory_service
        self.conversation_states = {}  # conversation_id -> GroupConversationState
        
    async def initialize_group_conversation(self, character_ids: List[str], 
                                          user_id: str, 
                                          topic: str = None) -> str:
        """Initialize a new group conversation"""
        
        conversation_id = f"group_{datetime.now().timestamp()}"
        
        # Load character personalities and relationships
        character_personalities = {}
        character_relationships = {}
        
        for char_id in character_ids:
            character_personalities[char_id] = await self._load_character_personality(char_id)
            
            # Load relationships between characters
            char_relationships = {}
            for other_char_id in character_ids:
                if other_char_id != char_id:
                    relationship = await self._get_character_relationship(char_id, other_char_id)
                    char_relationships[other_char_id] = relationship
            
            character_relationships[char_id] = char_relationships
        
        # Analyze group dynamics
        group_dynamics = await self._analyze_group_dynamics(
            character_ids, character_personalities, character_relationships
        )
        
        # Determine speaking order based on personalities and social dynamics
        speaking_order = self._determine_speaking_order(character_ids, group_dynamics)
        
        state = GroupConversationState(
            participants=character_ids + [user_id],
            conversation_history=[],
            current_speaker=speaking_order[0],
            speaking_order=speaking_order,
            conversation_topic=topic or "general discussion",
            group_dynamics=group_dynamics,
            interpersonal_relationships=character_relationships
        )
        
        self.conversation_states[conversation_id] = state
        
        return conversation_id
    
    async def process_group_message(self, conversation_id: str, 
                                  speaker_id: str, 
                                  message: str) -> List[Dict]:
        """Process a message in group conversation and generate responses"""
        
        state = self.conversation_states.get(conversation_id)
        if not state:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Create conversation turn
        turn = ConversationTurn(
            speaker_id=speaker_id,
            content=message,
            timestamp=datetime.now(),
            addressed_to=self._identify_addressees(message, state),
            references=self._identify_references(message, state),
            emotional_tone=await self._analyze_emotional_tone(message)
        )
        
        state.conversation_history.append(turn)
        
        # Generate responses from other participants
        responses = []
        
        # Determine who should respond based on:
        # 1. Who was addressed
        # 2. Social dynamics
        # 3. Personality traits
        # 4. Conversation flow
        
        potential_responders = self._determine_potential_responders(turn, state)
        
        for responder_id in potential_responders:
            if responder_id != speaker_id:  # Don't respond to self
                response = await self._generate_group_response(
                    responder_id, turn, state
                )
                if response:
                    responses.append(response)
        
        # Handle simultaneous responses (interruptions, agreements, etc.)
        simultaneous_responses = await self._generate_simultaneous_responses(
            turn, state, responses
        )
        responses.extend(simultaneous_responses)
        
        return responses
    
    async def _generate_group_response(self, character_id: str, 
                                     triggering_turn: ConversationTurn,
                                     state: GroupConversationState) -> Optional[Dict]:
        """Generate a response for a character in group conversation"""
        
        # Analyze the triggering message from character's perspective
        character_personality = state.group_dynamics['personalities'][character_id]
        
        # Consider relationships with speaker
        speaker_relationship = state.interpersonal_relationships[character_id].get(
            triggering_turn.speaker_id, {'familiarity': 0.5, 'affection': 0.5}
        )
        
        # Determine if character should respond
        response_probability = self._calculate_response_probability(
            character_id, triggering_turn, state, speaker_relationship
        )
        
        if response_probability < 0.3:  # Threshold for responding
            return None
        
        # Generate contextual prompt for character
        context_prompt = self._build_group_conversation_context(
            character_id, triggering_turn, state
        )
        
        # Generate response using character's personality
        response_content = await self.character_services[character_id].generate_response(
            context_prompt,
            include_group_dynamics=True
        )
        
        # Determine response style based on relationship and personality
        response_style = self._determine_response_style(
            character_id, triggering_turn, state, speaker_relationship
        )
        
        # Check for interruptions or agreements
        if self._should_interrupt(character_id, triggering_turn, state):
            response_content = self._add_interruption_markers(response_content)
        
        return {
            'character_id': character_id,
            'content': response_content,
            'style': response_style,
            'timestamp': datetime.now().isoformat(),
            'references': self._extract_references(response_content, state),
            'emotional_tone': await self._analyze_emotional_tone(response_content),
            'interruption': 'interruption' in response_style
        }
    
    def _build_group_conversation_context(self, character_id: str,
                                        triggering_turn: ConversationTurn,
                                        state: GroupConversationState) -> str:
        """Build comprehensive context for character response generation"""
        
        context_parts = []
        
        # Add character personality
        personality = state.group_dynamics['personalities'][character_id]
        context_parts.append(f"You are {personality['name']} with these traits: {personality['traits']}")
        
        # Add conversation context
        recent_history = state.conversation_history[-10:]
        context_parts.append("Recent conversation:")
        for turn in recent_history:
            speaker_name = state.group_dynamics['personalities'][turn.speaker_id]['name']
            context_parts.append(f"{speaker_name}: {turn.content}")
        
        # Add relationship context
        if triggering_turn.speaker_id in state.interpersonal_relationships[character_id]:
            relationship = state.interpersonal_relationships[character_id][triggering_turn.speaker_id]
            context_parts.append(f"Your relationship with {triggering_turn.speaker_id}: "
                               f"familiarity {relationship['familiarity']}, "
                               f"affection {relationship['affection']}")
        
        # Add current topic and dynamics
        context_parts.append(f"Current topic: {state.conversation_topic}")
        context_parts.append(f"Group dynamics: {state.group_dynamics['dominance_hierarchy']}")
        
        # Add triggering message
        speaker_name = state.group_dynamics['personalities'][triggering_turn.speaker_id]['name']
        context_parts.append(f"\n{speaker_name} just said: '{triggering_turn.content}'")
        
        # Add response guidance
        context_parts.append("\nRespond naturally in character, considering:")
        context_parts.append("- Your personality and relationship with the speaker")
        context_parts.append("- The conversation flow and topic")
        context_parts.append("- Other participants who might respond")
        context_parts.append("- Whether you agree, disagree, or want to add something")
        
        return "\n".join(context_parts)
    
    def _determine_response_style(self, character_id: str,
                                triggering_turn: ConversationTurn,
                                state: GroupConversationState,
                                relationship: Dict) -> Dict:
        """Determine how the character should respond"""
        
        personality = state.group_dynamics['personalities'][character_id]
        speaker_id = triggering_turn.speaker_id
        
        # Base style on personality
        if personality['traits'].get('agreeableness', 0.5) > 0.7:
            base_style = 'supportive and collaborative'
        elif personality['traits'].get('dominance', 0.5) > 0.7:
            base_style = 'assertive and leading'
        else:
            base_style = 'neutral and observational'
        
        # Adjust based on relationship
        if relationship['affection'] > 0.7:
            style_modifier = 'warm and friendly'
        elif relationship['affection'] < 0.3:
            style_modifier = 'distant and formal'
        else:
            style_modifier = 'professional and courteous'
        
        # Check for disagreement potential
        if self._detect_potential_disagreement(triggering_turn, character_id, state):
            if personality['traits'].get('openness', 0.5) < 0.3:
                style_modifier += ', potentially argumentative'
            else:
                style_modifier += ', diplomatically disagreeing'
        
        # Check for interruption
        interruption_likelihood = self._calculate_interruption_likelihood(
            character_id, triggering_turn, state
        )
        
        return {
            'base_style': base_style,
            'style_modifier': style_modifier,
            'interruption_probability': interruption_likelihood,
            'response_length': self._determine_response_length(personality, relationship)
        }
    
    async def _generate_simultaneous_responses(self, triggering_turn: ConversationTurn,
                                             state: GroupConversationState,
                                             existing_responses: List[Dict]) -> List[Dict]:
        """Generate responses that happen simultaneously (agreements, interruptions, etc.)"""
        
        simultaneous_responses = []
        
        # Check for agreements/disagreements
        for character_id in state.participants:
            if character_id == triggering_turn.speaker_id or character_id == 'user':
                continue
            
            # Agreement detection
            agreement_likelihood = await self._calculate_agreement_likelihood(
                character_id, triggering_turn, state
            )
            
            if agreement_likelihood > 0.7 and len(existing_responses) < 3:
                agreement_response = await self._generate_agreement_response(
                    character_id, triggering_turn, state
                )
                if agreement_response:
                    simultaneous_responses.append(agreement_response)
            
            # Interruption detection
            interruption_likelihood = await self._calculate_interruption_likelihood(
                character_id, triggering_turn, state
            )
            
            if interruption_likelihood > 0.6 and len(existing_responses) < 2:
                interruption_response = await self._generate_interruption_response(
                    character_id, triggering_turn, state
                )
                if interruption_response:
                    simultaneous_responses.append(interruption_response)
        
        return simultaneous_responses
    
    def _analyze_group_dynamics(self, character_ids: List[str],
                              personalities: Dict,
                              relationships: Dict) -> Dict:
        """Analyze social dynamics within the group"""
        
        dynamics = {
            'dominance_hierarchy': self._calculate_dominance_hierarchy(personalities),
            'social_cohesion': self._calculate_social_cohesion(relationships),
            'conflict_potential': self._calculate_conflict_potential(personalities, relationships),
            'conversation_flow_preference': self._determine_conversation_flow(personalities),
            'likely_alliances': self._identify_alliances(relationships),
            'potential_tension_points': self._identify_tension_points(relationships)
        }
        
        return dynamics