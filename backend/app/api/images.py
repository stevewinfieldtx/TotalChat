from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
import json
import asyncio

router = APIRouter()

RUNWARE_API_KEY = os.getenv('RUNWARE_API_KEY')
RUNWARE_API_URL = "https://api.runware.ai/v1"

class ImageGenerationRequest(BaseModel):
    characterId: str
    prompt: str
    emotion: Optional[str] = "neutral"
    negativePrompt: Optional[str] = "blurry, low quality, distorted"
    width: int = 512
    height: int = 768
    steps: int = 25
    guidanceScale: float = 7.5
    seed: Optional[int] = None

class ImageResponse(BaseModel):
    imageUrl: str
    imageId: str
    emotion: str
    prompt: str

@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate character image using Runware API"""
    if not RUNWARE_API_KEY:
        raise HTTPException(status_code=500, detail="Runware API key not configured")
    
    try:
        # Build the prompt with character context
        full_prompt = await build_character_prompt(request.characterId, request.prompt, request.emotion)
        
        # Call Runware API
        image_url = await call_runware_api(
            prompt=full_prompt,
            negative_prompt=request.negativePrompt,
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance_scale=request.guidanceScale,
            seed=request.seed
        )
        
        # Save to database/storage if needed
        # await save_character_image(request.characterId, image_url, request.emotion)
        
        return ImageResponse(
            imageUrl=image_url,
            imageId=f"{request.characterId}_{int(asyncio.get_event_loop().time())}",
            emotion=request.emotion,
            prompt=full_prompt
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

async def call_runware_api(
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    guidance_scale: float,
    seed: Optional[int] = None
) -> str:
    """Call Runware API to generate image"""
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Runware uses a task-based API
        request_payload = [
            {
                "taskType": "imageInference",
                "taskUUID": f"task_{int(asyncio.get_event_loop().time())}",
                "model": "runware:100@1",  # Adjust model as needed
                "positivePrompt": prompt,
                "negativePrompt": negative_prompt,
                "width": width,
                "height": height,
                "numberResults": 1,
                "steps": steps,
                "CFGScale": guidance_scale,
                "scheduler": "FlowMatchEulerDiscreteScheduler",
                "seed": seed if seed else None
            }
        ]
        
        response = await client.post(
            RUNWARE_API_URL,
            headers={
                "Authorization": f"Bearer {RUNWARE_API_KEY}",
                "Content-Type": "application/json"
            },
            json=request_payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Runware API error: {response.text}"
            )
        
        data = response.json()
        
        # Extract image URL from response
        if data and len(data) > 0 and 'imageURL' in data[0]:
            return data[0]['imageURL']
        else:
            raise HTTPException(status_code=500, detail="No image URL in Runware response")

async def build_character_prompt(character_id: str, base_prompt: str, emotion: str) -> str:
    """Build enhanced prompt based on character profile and emotion"""
    
    # Load character profile (you'll need to implement this)
    # character = await load_character_profile(character_id)
    
    # For now, use a basic template
    emotion_modifiers = {
        "happy": "smiling, cheerful expression, bright eyes",
        "sad": "melancholic expression, downcast eyes, gentle frown",
        "angry": "intense expression, furrowed brow, stern look",
        "neutral": "calm expression, relaxed face",
        "loving": "warm smile, affectionate gaze, soft expression",
        "excited": "energetic expression, wide eyes, bright smile"
    }
    
    modifier = emotion_modifiers.get(emotion, emotion_modifiers["neutral"])
    
    enhanced_prompt = f"{base_prompt}, {modifier}, high quality, detailed, professional photography"
    
    return enhanced_prompt

@router.get("/character/{character_id}/images")
async def get_character_images(character_id: str):
    """Get all images for a character"""
    try:
        # This should query your database for stored images
        # For now, return empty array
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upscale")
async def upscale_image(image_url: str, scale: int = 2):
    """Upscale an existing image using Runware"""
    if not RUNWARE_API_KEY:
        raise HTTPException(status_code=500, detail="Runware API key not configured")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            request_payload = [
                {
                    "taskType": "imageUpscale",
                    "taskUUID": f"upscale_{int(asyncio.get_event_loop().time())}",
                    "inputImage": image_url,
                    "upscaleFactor": scale
                }
            ]
            
            response = await client.post(
                RUNWARE_API_URL,
                headers={
                    "Authorization": f"Bearer {RUNWARE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_payload
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Runware upscale error: {response.text}"
                )
            
            data = response.json()
            
            if data and len(data) > 0 and 'imageURL' in data[0]:
                return {"imageUrl": data[0]['imageURL']}
            else:
                raise HTTPException(status_code=500, detail="No image URL in response")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove-background")
async def remove_background(image_url: str):
    """Remove background from image using Runware"""
    if not RUNWARE_API_KEY:
        raise HTTPException(status_code=500, detail="Runware API key not configured")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            request_payload = [
                {
                    "taskType": "imageBackgroundRemoval",
                    "taskUUID": f"bg_remove_{int(asyncio.get_event_loop().time())}",
                    "inputImage": image_url
                }
            ]
            
            response = await client.post(
                RUNWARE_API_URL,
                headers={
                    "Authorization": f"Bearer {RUNWARE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_payload
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Runware background removal error: {response.text}"
                )
            
            data = response.json()
            
            if data and len(data) > 0 and 'imageURL' in data[0]:
                return {"imageUrl": data[0]['imageURL']}
            else:
                raise HTTPException(status_code=500, detail="No image URL in response")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))