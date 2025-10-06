"""Local fallback implementation for ElevenLabs text-to-speech."""
from __future__ import annotations

import asyncio
import base64
from typing import Optional


class ElevenLabsService:
    """Generate speech audio payloads for websocket clients.

    The real project integrates with the ElevenLabs API.  To keep the backend
    functional in an offline environment we deterministically encode the
    requested text into a base64 payload that can be streamed to the frontend.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        self._encoding = encoding

    async def generate_speech(self, text: str, voice_id: Optional[str] = None) -> str:
        """Generate a base64 encoded audio payload.

        Parameters
        ----------
        text:
            The message to transform into speech.  Must be non-empty.
        voice_id:
            Identifier for the requested ElevenLabs voice.  The local fallback
            does not use the value directly but keeps the signature compatible
            with the production implementation.
        """

        if not text or not text.strip():
            raise ValueError("text must be a non-empty string")

        payload = {
            "voice": voice_id or "default",
            "text": text.strip(),
        }
        encoded_bytes = base64.b64encode(
            f"{payload['voice']}::{payload['text']}".encode(self._encoding)
        )

        await asyncio.sleep(0)
        return encoded_bytes.decode("ascii")