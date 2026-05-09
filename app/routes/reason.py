from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.reasoning import reason_about_transcript
from app.logger import logger
import time
import groq

router = APIRouter()

class ReasonRequest(BaseModel):
    transcript: str

@router.post("/reason")
async def reason(request: ReasonRequest):
    start_time = time.perf_counter()
    transcript = request.transcript.strip() if request.transcript else ""
    
    # Validate transcript presence
    if not transcript:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Transcript required",
                "pipeline_stage": "reasoning"
            }
        )
    
    try:
        # Call reasoning service
        result = await reason_about_transcript(transcript)
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        transcript_word_count = len(transcript.split())
        response_word_count = result["word_count"]
        
        logger.info(
            f"Reasoning success: transcript_words={transcript_word_count}, "
            f"response_words={response_word_count}, latency={latency_ms:.2f}ms"
        )
        
        return {
            "status": "ok",
            "response_text": result["response_text"],
            "word_count": response_word_count
        }
        
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Transcript too short to reason about":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": error_msg,
                    "pipeline_stage": "reasoning"
                }
            )
        elif error_msg == "Reasoning engine returned invalid response":
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "error": error_msg,
                    "pipeline_stage": "reasoning"
                }
            )
        raise e
        
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"Reasoning failed: {str(e)}", exc_info=True)
        
        if isinstance(e, (groq.GroqError, groq.APIError)):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "Reasoning service unavailable",
                    "detail": str(e),
                    "pipeline_stage": "reasoning"
                }
            )
            
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(e),
                "pipeline_stage": "reasoning"
            }
        )
