# backend/services/memory_service.py
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
import redis
from sqlalchemy.orm import Session
import openai

class MemoryService:
    def __init__(self, db: Session, redis_client: redis.Redis, embedding_model: SentenceTransformer):
        self.db = db
        self.redis = redis_client
        self.embedding_model = embedding_model
        self.memory_retention_days = 90
        self.max_memories_per_type = 100
        
    async def store_memory(self, memory: Memory) -> bool:
        """Store a new memory with embedding and relationship updates"""
        try:
            # Generate embedding
            memory.embedding = self.embedding_model.encode(memory.content).tolist()
            
            # Store in vector database (Pinecone/Milvus)
            await self._store_in_vector_db(memory)
            
            # Cache recent memories in Redis
            await self._cache_memory(memory)
            
            # Update relationship metrics
            await self._update_relationship_metrics(memory)
            
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    async def retrieve_relevant_memories(self, character_id: str, user_id: str, 
                                       query: str, limit: int = 10) -> List[Memory]:
        """Retrieve most relevant memories using hybrid search"""
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search in vector database
        vector_results = await self._search_vector_db(character_id, user_id, query_embedding, limit)
        
        # Get recent memories from Redis
        recent_memories = await self._get_recent_memories(character_id, user_id, hours=24)
        
        # Combine and rank results
        all_memories = self._rank_memories(vector_results + recent_memories, query_embedding)
        
        # Update access metrics
        for memory in all_memories[:limit]:
            await self._update_access_metrics(memory)
        
        return all_memories[:limit]
    
    async def extract_memories_from_conversation(self, character_id: str, user_id: str,
                                               conversation_history: List[Dict]) -> List[Memory]:
        """Extract meaningful memories from conversation using AI"""
        
        # Prepare conversation for analysis
        conversation_text = self._format_conversation(conversation_history)
        
        # Use AI to extract memories
        extraction_prompt = f"""
        Analyze this conversation between a user and {character_id}. 
        Extract important information that should be remembered for future interactions.
        
        Focus on:
        1. Personal details (name, interests, preferences, experiences)
        2. Emotional moments or significant events
        3. Opinions or beliefs expressed
        4. Relationship developments
        5. Shared experiences or inside jokes
        
        Conversation:
        {conversation_text}
        
        Return as JSON array with fields: type, content, priority, emotional_weight, tags
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3
        )
        
        extracted_data = json.loads(response.choices[0].message.content)
        memories = []
        
        for item in extracted_data:
            memory = Memory(
                id=f"{character_id}_{user_id}_{datetime.now().isoformat()}",
                character_id=character_id,
                user_id=user_id,
                memory_type=MemoryType(item["type"]),
                content=item["content"],
                priority=MemoryPriority(item["priority"]),
                emotional_weight=item.get("emotional_weight", 1.0),
                tags=item.get("tags", []),
                timestamp=datetime.now(),
                last_accessed=datetime.now()
            )
            memories.append(memory)
        
        return memories
    
    def _rank_memories(self, memories: List[Memory], query_embedding: np.ndarray) -> List[Memory]:
        """Rank memories based on relevance, recency, and importance"""
        
        for memory in memories:
            # Calculate semantic similarity
            memory_embedding = np.array(memory.embedding)
            semantic_score = np.dot(query_embedding, memory_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
            )
            
            # Calculate recency score (exponential decay)
            time_diff = datetime.now() - memory.timestamp
            recency_score = np.exp(-time_diff.days / 30)  # 30-day half-life
            
            # Calculate importance score
            importance_score = memory.priority.value * memory.emotional_weight * (1 + memory.access_count * 0.1)
            
            # Combined score
            memory.confidence = (
                semantic_score * 0.5 + 
                recency_score * 0.3 + 
                importance_score * 0.2
            )
        
        # Sort by confidence
        return sorted(memories, key=lambda x: x.confidence, reverse=True)
    
    async def _update_relationship_metrics(self, memory: Memory):
        """Update relationship metrics based on new memory"""
        
        relationship_key = f"relationship:{memory.character_id}:{memory.user_id}"
        relationship_data = await self.redis.hgetall(relationship_key)
        
        if not relationship_data:
            relationship_data = {
                'familiarity_score': 0.0,
                'trust_score': 0.5,
                'affection_score': 0.5,
                'shared_experiences': 0,
                'last_interaction': datetime.now().isoformat()
            }
        
        # Update familiarity based on memory type and frequency
        if memory.memory_type == MemoryType.SEMANTIC:
            relationship_data['familiarity_score'] = min(
                float(relationship_data['familiarity_score']) + 0.05, 1.0
            )
        
        # Update trust based on consistency and emotional weight
        if memory.emotional_weight > 1.5:  # Significant emotional moment
            relationship_data['trust_score'] = min(
                float(relationship_data['trust_score']) + 0.1, 1.0
            )
        
        # Update affection based on positive interactions
        if 'positive' in memory.tags or memory.emotional_weight > 1.0:
            relationship_data['affection_score'] = min(
                float(relationship_data['affection_score']) + 0.03, 1.0
            )
        
        relationship_data['shared_experiences'] = int(relationship_data['shared_experiences']) + 1
        relationship_data['last_interaction'] = datetime.now().isoformat()
        
        # Update relationship phase
        total_interactions = int(relationship_data['shared_experiences'])
        if total_interactions > 50:
            relationship_data['relationship_phase'] = 'intimate'
        elif total_interactions > 20:
            relationship_data['relationship_phase'] = 'close_friend'
        elif total_interactions > 5:
            relationship_data['relationship_phase'] = 'friend'
        elif total_interactions > 1:
            relationship_data['relationship_phase'] = 'acquaintance'
        
        await self.redis.hset(relationship_key, mapping=relationship_data)