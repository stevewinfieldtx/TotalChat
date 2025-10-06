"""Character data model used by the backend services."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Character:
    """Represents a conversational character configuration."""

    id: str
    name: str
    description: str
    personality: str
    speaking_style: str
    context: str
    model: str = "openrouter/auto"
    voice_enabled: bool = False
    voice_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.voice_enabled and not self.voice_id:
            raise ValueError("voice_id is required when voice_enabled is True")

        # Ensure metadata is a mutable copy even when a mapping is provided.
        object.__setattr__(self, "metadata", dict(self.metadata))