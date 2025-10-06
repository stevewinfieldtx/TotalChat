from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import json
from datetime import datetime

from models.character import Character
from services.openrouter_service import OpenRouterService
from services.runware_service import RunwareService
from services.elevenlabs_service import ElevenLabsService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    characters: List[Dict]
    conversation_history: List[Dict]

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

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Process message for each character
            for character_data in request["characters"]:
                character = Character(**character_data)
                
                # Generate response using OpenRouter
                response = await generate_character_response(
                    character, 
                    request["message"], 
                    request["conversation_history"]
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
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def generate_character_response(character: Character, message: str, history: List[Dict]) -> str:
    openrouter = OpenRouterService()
    
    prompt = f"""You are {character.name}, {character.description}.
    
    Personality: {character.personality}
    Speaking Style: {character.speaking_style}
    Historical Context: {character.context}
    
    Conversation History: {history}
    
    User Message: {message}
    
    Respond as {character.name} would, staying in character and maintaining historical accuracy."""
    
    return await openrouter.generate_response(prompt, character.model)

async def generate_voice(character: Character, text: str) -> bytes:
    elevenlabs = ElevenLabsService()
    return await elevenlabs.generate_speech(text, character.voice_id)