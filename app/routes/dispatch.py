from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.transcription import transcribe_audio
from app.services.reasoning import reason_about_transcript
from app.services.synthesis import synthesize_speech
from app.logger import logger
import time
import io
import groq

router = APIRouter()

ALLOWED_MIME_TYPES = [
    "audio/wav", "audio/wave", "audio/x-wav", 
    "audio/mpeg", "audio/mp3", 
    "audio/mp4", "audio/m4a", "audio/x-m4a",
    "video/mp4"
]

@router.post(
    "/dispatch-call",
    summary="End-to-end voice dispatch pipeline",
    description="""This is the primary entry point for the DispatchOS agent. It orchestrates a sequential pipeline where audio bytes are first converted to text via Groq Whisper, then passed to a LLaMA-3 reasoning engine that acts as a freight dispatcher, and finally converted back to speech via gTTS. This endpoint is designed for single-turn driver check-ins.

**Response Headers:**
- `X-Pipeline-Latency-Ms`: Total time taken for the entire request.
- `X-Transcription-Ms`: Time spent on speech-to-text processing.
- `X-Reasoning-Ms`: Time spent on LLM response generation.
- `X-Synthesis-Ms`: Time spent on text-to-speech synthesis.
- `X-Transcript-Preview`: A snippet of the transcribed driver speech.
- `X-TTS-Engine`: The voice engine used (defaults to gTTS).

If no speech is detected in the input audio, the system returns a 200 OK with a 'no_speech' JSON status message instead of audio.""",
    response_description="An audio stream (MPEG) containing the dispatcher's vocal response, or a JSON object if no speech was detected.",
    responses={
        200: {"description": "Pipeline executed successfully (audio returned) or no speech detected"},
        422: {"description": "Unsupported audio file type or invalid MIME type"},
        502: {"description": "Upstream stage error (transcription, reasoning, or synthesis failure)"},
        503: {"description": "External API service unavailable (Groq or gTTS connection issues)"},
        500: {"description": "Internal server error during pipeline orchestration"}
    }
)
async def dispatch_call(file: UploadFile = File(...)):
    start_total = time.monotonic()
    
    # 1. Validate mime type
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
        # 2. Transcription Stage
        start_transcription = time.monotonic()
        file_bytes = await file.read()
        
        try:
            trans_result = await transcribe_audio(file_bytes, file.filename)
            transcript = trans_result["transcript"]
        except ValueError as e:
            if str(e) == "Transcript text is empty":
                return {
                    "status": "no_speech",
                    "message": "No driver speech detected in audio"
                }
            raise e
            
        transcription_ms = (time.monotonic() - start_transcription) * 1000
        
        # 3. Reasoning Stage
        start_reasoning = time.monotonic()
        try:
            reason_result = await reason_about_transcript(transcript)
            response_text = reason_result["response_text"]
            word_count = reason_result["word_count"]
        except ValueError as e:
            # Re-raise to be caught by the outer block with reasoning stage
            raise e
            
        reasoning_ms = (time.monotonic() - start_reasoning) * 1000
        
        # 4. Synthesis Stage
        start_synthesis = time.monotonic()
        audio_bytes = await synthesize_speech(response_text)
        synthesis_ms = (time.monotonic() - start_synthesis) * 1000
        
        total_latency_ms = (time.monotonic() - start_total) * 1000
        transcript_preview = transcript[:60]
        
        # Logging
        logger.info(
            f"Dispatch pipeline success: filename={file.filename}, "
            f"total_latency={total_latency_ms:.2f}ms, trans_ms={transcription_ms:.2f}ms, "
            f"reason_ms={reasoning_ms:.2f}ms, synth_ms={synthesis_ms:.2f}ms, "
            f"preview='{transcript_preview}', words={word_count}"
        )
        
        # Response with headers
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "X-Pipeline-Latency-Ms": f"{total_latency_ms:.2f}",
                "X-Transcription-Ms": f"{transcription_ms:.2f}",
                "X-Reasoning-Ms": f"{reasoning_ms:.2f}",
                "X-Synthesis-Ms": f"{synthesis_ms:.2f}",
                "X-Transcript-Preview": transcript_preview,
                "X-TTS-Engine": "gTTS"
            }
        )
        
    except Exception as e:
        # Determine pipeline stage
        stage = "unknown"
        # Based on where the error likely occurred
        # Since I'm using nested try blocks for specific logic, I can track stage
        # But a simpler way is to check the type or use a variable
        
        # If we didn't reach reasoning, it was transcription
        if 'transcription_ms' not in locals():
            stage = "transcription"
        elif 'reasoning_ms' not in locals():
            stage = "reasoning"
        else:
            stage = "synthesis"
            
        logger.error(f"Pipeline failed at {stage}: {str(e)}", exc_info=True)
        
        # Handle specific error types
        if isinstance(e, (groq.GroqError, groq.APIError)):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            msg = f"{stage.capitalize()} service unavailable"
        elif isinstance(e, ValueError) or isinstance(e, RuntimeError):
            status_code = status.HTTP_502_BAD_GATEWAY
            msg = str(e)
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            msg = str(e)
            
        return JSONResponse(
            status_code=status_code,
            content={
                "error": msg,
                "pipeline_stage": stage
            }
        )
