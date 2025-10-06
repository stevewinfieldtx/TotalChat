"""Utility class for generating LLM responses via OpenRouter (with fallback)."""
from __future__ import annotations

import asyncio
import os
import re
from typing import Callable, Optional

import httpx
import logging

logger = logging.getLogger("openrouter")


class OpenRouterService:
    """High-level wrapper around the OpenRouter API with a local fallback."""

    def __init__(self, response_generator: Optional[Callable[[str, str], str]] = None) -> None:
        self._response_generator = response_generator
        self._api_key = os.getenv("OPENROUTER_API_KEY")
        self._api_url = os.getenv(
            "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
        )
        # Env var names expected by OpenRouter docs
        # OPENROUTER_API_KEY is the only required one. The HTTP-Referer and X-Title
        # headers are optional but recommended; use sane defaults if missing.
        self._http_referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("HTTP_REFERER") or "http://localhost"
        self._app_title = os.getenv("OPENROUTER_APP_TITLE") or os.getenv("APP_TITLE") or "AI Influencer Platform"
        self._strict = (os.getenv("OPENROUTER_STRICT", "0") == "1")
        if not self._api_key:
            logger.warning("OpenRouter: OPENROUTER_API_KEY not set; using local fallback responses.")

    async def generate_response(self, prompt: str, model: str) -> str:
        """Generate a model response for the supplied prompt.

        Uses the OpenRouter API when an API key is configured; otherwise falls
        back to a deterministic local generator so the app remains usable
        offline.
        """

        if not prompt or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        if self._api_key:
            try:
                logger.info("OpenRouter: calling model=%s", model or "openrouter/auto")
                content = await self._call_openrouter(prompt, model)
                if content and isinstance(content, str):
                    logger.info("OpenRouter: response received (%d chars)", len(content))
                    return content.strip()
            except Exception as exc:
                # If the API call fails, optionally raise in strict mode
                if self._strict:
                    logger.exception("OpenRouter call failed (strict mode): %s", exc)
                    raise
                logger.exception("OpenRouter call failed; falling back to local generator: %s", exc)

        # Fallback path
        generator = self._response_generator or self._default_response
        response = generator(prompt, model)
        if not isinstance(response, str) or not response.strip():
            raise ValueError("response generator returned empty output")
        await asyncio.sleep(0)
        return response.strip()

    async def _call_openrouter(self, prompt: str, model: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._http_referer,
            "X-Title": self._app_title,
        }

        payload = {
            "model": model or "openrouter/auto",
            "messages": [
                {"role": "system", "content": "You are a conversational character. Stay in persona and be helpful."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.8,
            "max_tokens": 400,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self._api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # OpenRouter chat completions format
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

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