"""CLI helper for exercising the websocket chat endpoint locally."""
from __future__ import annotations

import argparse
import asyncio
import json
from typing import Iterable, List, Dict, Any

import websockets


DEFAULT_CHARACTERS: List[Dict[str, Any]] = [
    {
        "id": "ada",
        "name": "Ada Lovelace",
        "description": "a pioneering mathematician and writer with a love for analytical thinking",
        "personality": "Curious, methodical, and supportive",
        "speaking_style": "Elegant Victorian era prose with a scientific undertone",
        "context": "Mid-1800s London during the early days of computing",
        "model": "openrouter/auto",
        "voice_enabled": False,
    }
]


async def run_chat(message: str, characters: Iterable[Dict[str, Any]], uri: str) -> None:
    """Send a message to the websocket chat endpoint and print responses."""
    characters = list(characters)
    if not characters:
        raise ValueError("At least one character is required")

    async with websockets.connect(uri) as websocket:
        payload = {
            "message": message,
            "characters": characters,
            "conversation_history": [],
        }
        await websocket.send(json.dumps(payload))

        pending = {character["id"] for character in characters}
        while pending:
            raw = await websocket.recv()
            data = json.loads(raw)

            msg_type = data.get("type")
            if msg_type == "character_response":
                character_id = data["characterId"]
                pending.discard(character_id)
                content = data.get("content", "")
                print(f"\n[{character_id}] {content}\n")
            elif msg_type == "voice_data":
                character_id = data.get("characterId")
                print(
                    f"[debug] received voice data placeholder for {character_id}; "
                    "saving audio is not implemented in this helper."
                )
            else:
                print(f"[debug] received unhandled message: {data}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "message",
        nargs="?",
        default="Hello there! What inspires your work?",
        help="Message to send to the character(s).",
    )
    parser.add_argument(
        "--uri",
        default="ws://127.0.0.1:8000/ws/local-client",
        help="Websocket endpoint for the running backend server.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run_chat(args.message, DEFAULT_CHARACTERS, args.uri))


if __name__ == "__main__":
    main()