from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import health_router
from app.routes.transcribe import router as transcribe_router
from app.routes.reason import router as reason_router
from app.routes.synthesize import router as synthesize_router
from app.routes.dispatch import router as dispatch_router
from app.routes.apidocs import router as apidocs_router
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up freight-voice-agent...")
    yield
    # Shutdown logic
    logger.info("Shutting down freight-voice-agent...")

app = FastAPI(
    title="DispatchOS",
    description="""AI-native inbound voice dispatcher agent. Handles driver
    calls end-to-end: speech-to-text via Groq Whisper, freight-context
    reasoning via LLaMA, voice response via gTTS. Built as a prototype
    of the inbound ops layer for freight AI platforms.""",
    version="0.1.0",
    contact={
        "name": "Hardik Gayner",
        "url": "https://hardikgayner.vercel.app"
    },
    lifespan=lifespan
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(transcribe_router, prefix="/api/v1")
app.include_router(reason_router, prefix="/api/v1")
app.include_router(synthesize_router, prefix="/api/v1")
app.include_router(dispatch_router, prefix="/api/v1")
app.include_router(apidocs_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Freight Voice Agent API is running"}
