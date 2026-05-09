import io
import asyncio
from gtts import gTTS

async def synthesize_speech(text: str) -> bytes:
    """
    Synthesizes speech from text using gTTS (Google Text-to-Speech).
    
    Args:
        text: The text to synthesize.
        
    Returns:
        bytes: The synthesized audio in MP3 format.
        
    Raises:
        ValueError: If text is empty or too long.
        RuntimeError: If synthesis fails to produce audio.
    """
    if not text.strip():
        raise ValueError("Cannot synthesize empty text")
        
    if len(text) > 500:
        raise ValueError("Text too long for voice synthesis. Max 500 characters.")
        
    def _synthesis_task():
        tts = gTTS(text=text, lang="en", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()

    loop = asyncio.get_event_loop()
    audio_bytes = await loop.run_in_executor(None, _synthesis_task)
    
    if not audio_bytes:
        raise RuntimeError("Voice synthesis returned empty audio")
        
    return audio_bytes
