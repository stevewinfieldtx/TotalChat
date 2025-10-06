import base64

import pytest

from backend.services.elevenlabs_service import ElevenLabsService
from backend.services.openrouter_service import OpenRouterService


def test_openrouter_generates_persona_aware_response():
    service = OpenRouterService()
    prompt = (
        "You are Luna, a thoughtful space navigator.\n"
        "\nPersonality: calm and observant\n"
        "\nUser Message: \"How is the journey going?\""
    )

    response = asyncio.run(service.generate_response(prompt, "test-model"))

    assert "Luna" in response
    assert "How is the journey going?" in response
    assert "test-model" in response


def test_openrouter_rejects_empty_prompt():
    service = OpenRouterService()
    with pytest.raises(ValueError):
        asyncio.run(service.generate_response(" ", "model"))


def test_elevenlabs_generates_base64_audio():
    service = ElevenLabsService()
    payload = asyncio.run(service.generate_speech("Hello world", voice_id="voice123"))

    decoded = base64.b64decode(payload.encode("ascii")).decode("utf-8")
    assert decoded.startswith("voice123::")
    assert decoded.endswith("Hello world")


def test_elevenlabs_requires_text():
    service = ElevenLabsService()
    with pytest.raises(ValueError):
        asyncio.run(service.generate_speech("", voice_id=None))