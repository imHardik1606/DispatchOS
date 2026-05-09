from groq import AsyncGroq
from app.config import settings
import io

async def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    """
    Transcribes audio using Groq's Whisper API.
    
    Args:
        file_bytes: Raw bytes of the audio file.
        filename: Original filename of the audio file.
        
    Returns:
        dict: Transcription results containing transcript, duration hint, and character count.
        
    Raises:
        ValueError: If the transcription result is empty.
    """
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    # Use io.BytesIO to create a file-like object for the SDK
    audio_file = (filename, io.BytesIO(file_bytes))
    
    transcription = await client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3"
    )
    
    text = transcription.text.strip() if transcription.text else ""
    
    # Filter common Whisper hallucinations on silent/noisy audio
    hallucinations = {"you", "you.", "thank you", "thank you.", "thanks for watching", "subtitles by"}
    if text.lower() in hallucinations:
        text = ""
    
    if not text:
        raise ValueError("Transcript text is empty")
        
    return {
        "transcript": text,
        "duration_hint": "unknown",
        "char_count": len(text)
    }
