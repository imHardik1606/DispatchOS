from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import health_router
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up freight-voice-agent...")
    yield
    # Shutdown logic
    logger.info("Shutting down freight-voice-agent...")

app = FastAPI(
    title="freight-voice-agent",
    lifespan=lifespan
)

# Include routers
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Freight Voice Agent API is running"}
