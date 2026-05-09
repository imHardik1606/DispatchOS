from groq import AsyncGroq
from app.config import settings
from app.prompts.dispatcher import DISPATCHER_SYSTEM_PROMPT

async def reason_about_transcript(transcript: str) -> dict:
    """
    Analyzes a transcript and generates a dispatcher response using LLM.
    
    Args:
        transcript: The text transcript of the driver's speech.
        
    Returns:
        dict: The response text and word count.
        
    Raises:
        ValueError: If transcript is too short or LLM response is empty.
    """
    words = transcript.split()
    if len(words) < 3:
        raise ValueError("Transcript too short to reason about")
        
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": DISPATCHER_SYSTEM_PROMPT},
            {"role": "user", "content": transcript}
        ],
        temperature=0.0
    )
    
    response_text = response.choices[0].message.content.strip() if response.choices else ""
    
    if not response_text:
        raise ValueError("Reasoning engine returned invalid response")
        
    return {
        "response_text": response_text,
        "word_count": len(response_text.split())
    }
