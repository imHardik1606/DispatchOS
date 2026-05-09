from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from app.services.synthesis import synthesize_speech
from app.logger import logger
import io
import time

router = APIRouter()

class SynthesizeRequest(BaseModel):
    text: str

@router.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    start_time = time.perf_counter()
    text = request.text.strip() if request.text else ""
    
    # Validate text presence
    if not text:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Cannot synthesize empty text",
                "pipeline_stage": "synthesis"
            }
        )
        
    # Validate text length
    if len(text) > 500:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Text too long for voice synthesis. Max 500 characters.",
                "received_length": len(text),
                "pipeline_stage": "synthesis"
            }
        )
    
    try:
        # Call synthesis service
        audio_bytes = await synthesize_speech(text)
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        audio_size = len(audio_bytes)
        
        logger.info(
            f"Synthesis success: text_length={len(text)}, "
            f"audio_size={audio_size} bytes, latency={latency_ms:.2f}ms"
        )
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "X-Audio-Length-Bytes": str(audio_size),
                "X-TTS-Engine": "gTTS"
            }
        )
        
    except ValueError as e:
        # This handles cases where validation in service fails (should be covered by route validation but good to have)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": str(e),
                "pipeline_stage": "synthesis"
            }
        )
        
    except RuntimeError as e:
        # This handles empty audio bytes
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "error": str(e),
                "pipeline_stage": "synthesis"
            }
        )
        
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"Synthesis failed: {str(e)}", exc_info=True)
        
        # This handles connection errors or other gTTS failures
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Voice synthesis unavailable",
                "detail": str(e),
                "pipeline_stage": "synthesis"
            }
        )
