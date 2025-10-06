"""Utility helpers for working with avatar generation services."""
from __future__ import annotations

import asyncio
from typing import Dict

from models.character import Character


class RunwareService:
    """Provide deterministic prompts for downstream avatar generation."""

    async def build_avatar_prompt(self, character: Character) -> Dict[str, str]:
        """Create a structured prompt for the Runware image generator."""

        if not isinstance(character, Character):
            raise TypeError("character must be an instance of Character")

        await asyncio.sleep(0)
        return {
            "title": f"Portrait of {character.name}",
            "description": character.description,
            "style": character.speaking_style,
        }