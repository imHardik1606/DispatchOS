from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "freight-voice-agent",
        "tts_engine": "gTTS",
        "env_check": {
            "GROQ_API_KEY": bool(settings.GROQ_API_KEY)
        }
    }
