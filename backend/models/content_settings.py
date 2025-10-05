# backend/models/content_settings.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

class ContentLevel(Enum):
    SAFE = "safe"                    # No adult content
    SUGGESTIVE = "suggestive"        # Mild suggestive content
    MATURE = "mature"               # Adult themes, no explicit content
    EXPLICIT = "explicit"           # Explicit adult content

class NSFWContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

@dataclass
class ContentPolicy:
    user_id: str
    content_level: ContentLevel
    age_verified: bool
    verification_date: Optional[datetime]
    verification_method: Optional[str]
    restricted_categories: List[str]
    custom_filters: List[str]
    parental_controls: Optional[Dict]
    audit_log: List[Dict]

@dataclass
class ContentAnalysis:
    content_type: NSFWContentType
    is_nsfw: bool
    confidence_score: float
    categories: List[str]
    severity_level: int  # 1-10
    flagged_words: List[str]
    suggested_action: str
    explanation: str