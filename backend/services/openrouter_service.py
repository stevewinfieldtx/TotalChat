"""Utility class for generating LLM responses for characters."""
from __future__ import annotations

import asyncio
import re
from typing import Callable, Optional


class OpenRouterService:
    """High level wrapper around an OpenRouter-compatible client.

    The production project talks to the OpenRouter API, however the testing
    environment within this kata does not have network access nor API keys.
    To keep the server runnable we provide a small deterministic fallback that
    still produces character-aware responses.
    """

    def __init__(self, response_generator: Optional[Callable[[str, str], str]] = None) -> None:
        self._response_generator = response_generator

    async def generate_response(self, prompt: str, model: str) -> str:
        """Generate a model response for the supplied prompt.

        Parameters
        ----------
        prompt:
            Fully formatted prompt containing persona information and the
            user's latest message.
        model:
            The model identifier requested by the caller.

        Returns
        -------
        str
            A synthetic response that mirrors the persona details.
        """

        if not prompt or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        generator = self._response_generator or self._default_response
        response = generator(prompt, model)

        if not isinstance(response, str) or not response.strip():
            raise ValueError("response generator returned empty output")

        # Maintain the coroutine interface expected by the rest of the code.
        await asyncio.sleep(0)
        return response.strip()

    def _default_response(self, prompt: str, model: str) -> str:
        persona = self._extract(prompt, r"You are\s+(?P<value>.+?)\.") or "The character"
        message = self._extract(prompt, r"User Message:\s*(?P<value>.+)") or prompt

        cleaned_persona = " ".join(persona.split())
        cleaned_message = self._clean_message(message)

        return (
            f"{cleaned_persona} ({model}) reflects on the conversation and replies to "
            f"the user by acknowledging '{cleaned_message}'."
        )

    @staticmethod
    def _extract(prompt: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, prompt, re.DOTALL)
        if match:
            return match.group("value").strip()
        return None

    @staticmethod
    def _clean_message(message: str) -> str:
        message = message.strip()
        if message.startswith("\"") and message.endswith("\""):
            return message[1:-1].strip()
        return message