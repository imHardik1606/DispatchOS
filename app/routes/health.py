from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get(
    "/health",
    summary="Service health check",
    description="Verify the API is responsive and check the status of required environment variables like GROQ_API_KEY. Used by deployment platforms to monitor service availability.",
    response_description="Returns the service status and configuration state.",
    responses={
        200: {"description": "Service is healthy and dependencies are configured"}
    }
)
async def health_check():
    return {
        "status": "ok",
        "service": "DispatchOS (freight-voice-agent)",
        "tts_engine": "gTTS",
        "env_check": {
            "GROQ_API_KEY": bool(settings.GROQ_API_KEY)
        }
    }
