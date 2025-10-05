# backend/models/memory.py
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np

class MemoryType(Enum):
    EPISODIC = "episodic"      # Specific events/interactions
    SEMANTIC = "semantic"      # General knowledge about user
    EMOTIONAL = "emotional"    # Emotional experiences
    RELATIONAL = "relational"  # Relationships with other characters
    CONTEXTUAL = "contextual"  # Situational context

class MemoryPriority(Enum):
    HIGH = 3      # Critical information
    MEDIUM = 2    # Important details
    LOW = 1       # General information

class Memory(BaseModel):
    id: str
    character_id: str
    user_id: str
    memory_type: MemoryType
    content: str
    embedding: List[float] = Field(default_factory=list)
    emotional_weight: float = 1.0
    priority: MemoryPriority = MemoryPriority.MEDIUM
    timestamp: datetime
    last_accessed: datetime
    access_count: int = 0
    tags: List[str] = Field(default_factory=list)
    related_memories: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    source: str = "conversation"  # conversation, observation, inference

class Relationship(BaseModel):
    character_id: str
    user_id: str
    familiarity_score: float = 0.0  # 0-1 scale
    trust_score: float = 0.5        # 0-1 scale
    affection_score: float = 0.5    # 0-1 scale
    respect_score: float = 0.5      # 0-1 scale
    shared_experiences: int = 0
    last_interaction: datetime
    interaction_frequency: float = 0.0  # interactions per day
    relationship_phase: str = "stranger"  # stranger, acquaintance, friend, close_friend, intimate
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    conversation_topics: List[str] = Field(default_factory=list)
    emotional_connections: List[str] = Field(default_factory=list)