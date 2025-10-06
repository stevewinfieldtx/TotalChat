import pytest

from models.character import Character


def test_character_defaults():
    character = Character(
        id="char-1",
        name="Ava",
        description="an empathetic AI guide",
        personality="warm and encouraging",
        speaking_style="casual",
        context="set in a futuristic city",
    )

    assert character.model == "openrouter/auto"
    assert character.metadata == {}
    assert character.voice_enabled is False
    assert character.voice_id is None


def test_voice_configuration_requires_voice_id():
    with pytest.raises(ValueError):
        Character(
            id="char-voice",
            name="Nova",
            description="a narrator",
            personality="stoic",
            speaking_style="formal",
            context="narration",
            voice_enabled=True,
        )