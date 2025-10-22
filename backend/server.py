"""FastAPI websocket server for relaying character conversations."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

from models.character import Character
from .services.openrouter_service import OpenRouterService
from .services.runware_service import RunwareService
from .services.elevenlabs_service import ElevenLabsService

# Ensure we load env vars from the backend directory specifically
_BACKEND_ENV = Path(__file__).resolve().parent / ".env"
load_dotenv(_BACKEND_ENV, override=False)

app = FastAPI()

# Serve frontend static files (for production deployment)
_FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

# Route our OpenRouter logs through Uvicorn's logger so they show up
_uvicorn_logger = logging.getLogger("uvicorn.error")
_openrouter_logger = logging.getLogger("openrouter")
_openrouter_logger.setLevel(logging.INFO)
if _uvicorn_logger.handlers:
    _openrouter_logger.handlers = _uvicorn_logger.handlers
    _openrouter_logger.propagate = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("CORS_ORIGIN", "http://localhost:3000"),
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    """Schema describing incoming websocket messages from the UI."""

    message: str
    characters: List[Dict]
    conversation_history: List[Dict] = Field(default_factory=list)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()
openrouter_service = OpenRouterService()
elevenlabs_service = ElevenLabsService()
runware_service = RunwareService()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                if hasattr(ChatRequest, "model_validate_json"):
                    request = ChatRequest.model_validate_json(data)  # Pydantic v2
                else:
                    request = ChatRequest.parse_raw(data)  # type: ignore[attr-defined]
            except (ValidationError, ValueError) as exc:
                if isinstance(exc, ValidationError):
                    details = json.loads(exc.json())
                else:
                    details = str(exc)
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "invalid_payload",
                        "details": details,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                continue

            # Process message for each character
            for character_data in request.characters:
                try:
                    character = _build_character_from_payload(character_data)
                except (TypeError, ValueError) as exc:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": "invalid_character",
                            "details": str(exc),
                            "characterId": character_data.get("id"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                # Generate response using OpenRouter
                response = await generate_character_response(
                    character,
                    request.message,
                    request.conversation_history,
                )
                

                # Send character response
                await websocket.send_json({
                    "type": "character_response",
                    "characterId": character.id,
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate voice if enabled
                if character.voice_enabled:
                    voice_data = await generate_voice(character, response)
                    await websocket.send_json({
                        "type": "voice_data",
                        "characterId": character.id,
                        "audioData": voice_data
                    })
                
                avatar_prompt = await generate_avatar_prompt(character)
                await websocket.send_json(
                    {
                        "type": "avatar_prompt",
                        "characterId": character.id,
                        "prompt": avatar_prompt,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def generate_character_response(character: Character, message: str, history: List[Dict]) -> str:
    _uvicorn_logger.info("generate_character_response: model=%s name=%s", character.model, character.name)
    prompt = f"""You are {character.name}, {character.description}.
    
    Personality: {character.personality}
    Speaking Style: {character.speaking_style}
    Historical Context: {character.context}
    
    Conversation History: {history}
    
    User Message: {message}
    
    Respond as {character.name} would, staying in character and maintaining historical accuracy."""
    
    # Prefer a direct OpenRouter call; fall back to local generator on error
    resolved_model = character.model or "x-ai/grok-4-fast"
    try:
        content = await openrouter_service._call_openrouter(prompt, resolved_model)  # type: ignore[attr-defined]
        if content and isinstance(content, str) and content.strip():
            _uvicorn_logger.info("generate_character_response: openrouter ok (%d chars)", len(content))
            return content.strip()
    except Exception as exc:
        _uvicorn_logger.exception("generate_character_response: openrouter error -> falling back: %s", exc)

    # Fallback path via service wrapper (deterministic local generator)
    response = await openrouter_service.generate_response(prompt, resolved_model)
    _uvicorn_logger.info("generate_character_response: fallback response (%d chars)", len(response or ""))
    return response

async def generate_voice(character: Character, text: str) -> str:
    return await elevenlabs_service.generate_speech(text, character.voice_id)
async def generate_avatar_prompt(character: Character) -> Dict[str, str]:
    return await runware_service.build_avatar_prompt(character)


def _build_character_from_payload(data: Dict) -> Character:
    """Create a Character from a potentially partial client payload.

    Frontend may only send a subset of fields (id, name, title, images).
    This helper fills sensible defaults for the rest so the backend remains
    robust while the UI evolves.
    """

    # Attempt to hydrate from local JSON if category/id provided
    category = data.get("category")
    char_id = data.get("id")
    if category and char_id:
        json_path = _characters_root() / category / f"{char_id}.json"
        if json_path.exists():
            try:
                raw = json.loads(json_path.read_text(encoding="utf-8"))
                name = (
                    raw.get("name")
                    or (raw.get("core_identity") or {}).get("name")
                    or data.get("name")
                    or "Character"
                )
                description = (
                    raw.get("description")
                    or (raw.get("core_identity") or {}).get("profession")
                    or data.get("title")
                    or "A conversational persona."
                )
                dominant = (raw.get("psychological_profile") or {}).get("dominant_traits") or []
                personality = ", ".join(dominant) if isinstance(dominant, list) and dominant else data.get("personality") or "Helpful, friendly, and curious."
                speaking_style = (
                    (raw.get("communication_style") or {}).get("tone_and_cadence")
                    or (raw.get("voice_profile") or {}).get("tone")
                    or data.get("speaking_style")
                    or "Clear, concise, and engaging."
                )
                context = (
                    (raw.get("backstory_and_life_experiences") or {}).get("education_and_training")
                    or (raw.get("interaction_guidelines") or {}).get("chat_behavior")
                    or data.get("context")
                    or ""
                )
                # Extract LLM model from various possible locations, default to x-ai/grok-4-fast
                llm_model = (
                    raw.get("llm")
                    or raw.get("model")
                    or (raw.get("metadata") or {}).get("llm")
                    or (raw.get("metadata") or {}).get("model")
                    or data.get("model")
                    or "x-ai/grok-4-fast"
                )
                voice_enabled = bool(data.get("voice_enabled", False))
                voice_id = data.get("voice_id") if voice_enabled else None
                return Character(
                    id=str(char_id),
                    name=str(name),
                    description=str(description),
                    personality=str(personality),
                    speaking_style=str(speaking_style),
                    context=str(context),
                    model=str(llm_model),
                    voice_enabled=voice_enabled,
                    voice_id=voice_id,
                    metadata=data.get("metadata", {}),
                )
            except Exception:
                pass

    name = data.get("name") or data.get("character_name") or "Character"
    description = (
        data.get("description")
        or data.get("title")
        or "A conversational persona."
    )
    voice_enabled = bool(data.get("voice_enabled", False))
    voice_id = data.get("voice_id") if voice_enabled else None

    return Character(
        id=str(data.get("id") or name.lower().replace(" ", "_")),
        name=name,
        description=description,
        personality=data.get("personality", "Helpful, friendly, and curious."),
        speaking_style=data.get("speaking_style", "Clear, concise, and engaging."),
        context=data.get("context", ""),
        model=data.get("model", "x-ai/grok-4-fast"),
        voice_enabled=voice_enabled,
        voice_id=voice_id,
        metadata=data.get("metadata", {}),
    )


# -------- Development helpers: list and fetch local characters -------- #

def _characters_root() -> Path:
    # project root is one level above backend/ directory
    return Path(__file__).resolve().parents[1] / "public" / "characters"


@app.get("/api/characters/categories")
async def list_categories() -> Dict[str, List[str]]:
    root = _characters_root()
    categories = [p.name for p in root.iterdir() if p.is_dir()]
    return {"categories": sorted(categories)}


@app.get("/api/characters/{category}")
async def list_characters(category: str) -> Dict[str, List[Dict[str, Any]]]:
    root = _characters_root() / category
    if not root.exists() or not root.is_dir():
        return {"characters": []}

    results: List[Dict[str, Any]] = []
    for file in sorted(root.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        name = (
            data.get("name")
            or (data.get("core_identity") or {}).get("name")
            or (data.get("metadata") or {}).get("character_name")
            or file.stem
        )
        title = (
            data.get("title")
            or (data.get("core_identity") or {}).get("profession")
            or (data.get("metadata") or {}).get("model_id")
            or "Character"
        )
        char_id = file.stem
        images = [
            f"https://api.dicebear.com/7.x/avataaars/svg?seed={char_id}",
            f"https://api.dicebear.com/7.x/avataaars/svg?seed={char_id}2",
            f"https://api.dicebear.com/7.x/avataaars/svg?seed={char_id}3",
        ]
        results.append({
            "id": char_id,
            "name": name,
            "title": title,
            "images": images,
            "category": category,
        })
    return {"characters": results}


@app.get("/api/characters/{category}/{char_id}")
async def fetch_character(category: str, char_id: str) -> Dict[str, Any]:
    path = _characters_root() / category / f"{char_id}.json"
    if not path.exists():
        return {"error": "not_found"}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/debug/openrouter")
async def debug_openrouter() -> Dict[str, Any]:
    """Quick check that env is loaded and OpenRouter is configured."""
    return {
        "has_api_key": bool(os.getenv("OPENROUTER_API_KEY")),
        "api_url": os.getenv(
            "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
        ),
        "http_referer": os.getenv("OPENROUTER_HTTP_REFERER"),
        "app_title": os.getenv("OPENROUTER_APP_TITLE"),
        "cors_origin": os.getenv("CORS_ORIGIN"),
    }


@app.get("/debug/openrouter/ping")
async def debug_openrouter_ping() -> Dict[str, Any]:
    """Attempt a minimal OpenRouter call to verify connectivity."""
    svc = openrouter_service
    if not os.getenv("OPENROUTER_API_KEY"):
        return {"ok": False, "reason": "no_api_key"}
    try:
        # Call the API directly; if it fails we'll return the error
        content = await svc._call_openrouter("Reply with the single word: pong", "openrouter/auto")  # type: ignore[attr-defined]
        return {"ok": True, "content": content}
    except Exception as exc:
        return {"ok": False, "reason": "api_error", "detail": str(exc)}


# Serve frontend index.html for all other routes (SPA support)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the frontend React app for all non-API routes."""
    # If the frontend dist exists, serve index.html
    if _FRONTEND_DIST.exists():
        index_file = _FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    # Fallback for development or if frontend not built
    return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}