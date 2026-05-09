from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.transcription import transcribe_audio
from app.logger import logger
import time
import groq

router = APIRouter()

ALLOWED_MIME_TYPES = [
    "audio/wav", "audio/wave", "audio/x-wav", 
    "audio/mpeg", "audio/mp3", 
    "audio/mp4", "audio/x-m4a"
]

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    start_time = time.perf_counter()
    
    # Validate mime type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Unsupported file type",
                "accepted": ["wav", "mp3", "m4a"],
                "received": file.content_type
            }
        )
    
    try:
        # Read file bytes asynchronously
        file_bytes = await file.read()
        file_size_kb = len(file_bytes) / 1024
        
        try:
            result = await transcribe_audio(file_bytes, file.filename)
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            char_count = result["char_count"]
            
            logger.info(
                f"Transcription success: filename={file.filename}, "
                f"size={file_size_kb:.2f}KB, char_count={char_count}, "
                f"latency={latency_ms:.2f}ms"
            )
            
            return {
                "status": "ok",
                "transcript": result["transcript"],
                "char_count": char_count
            }
            
        except ValueError as e:
            # Handle empty transcript
            if str(e) == "Transcript text is empty":
                return {
                    "status": "empty_transcript",
                    "transcript": "",
                    "warning": "No driver speech detected in audio"
                }
            raise e
            
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        
        # Check if it's a Groq SDK exception
        if isinstance(e, (groq.GroqError, groq.APIError)):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "Transcription service unavailable",
                    "detail": str(e),
                    "pipeline_stage": "transcription"
                }
            )
        
        # Re-raise other exceptions to be handled by FastAPI's default handler or handle them here
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
