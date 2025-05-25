import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine

# Import configuration
from backend.config import get_config

# Import routers
from backend.api.tasks import router as tasks_router
from backend.api.auth import router as auth_router
from backend.api.assistant import router as assistant_router
from backend.api.settings import router as settings_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = get_config()
logger.info(f"Application configuration loaded. Debug mode: {config['debug']}")

# Set Gemini API key for web search integration
if config['api_keys']['gemini']:
    os.environ['GEMINI_API_KEY'] = config['api_keys']['gemini']
    logger.info("Gemini API key set for web search integration")
else:
    logger.warning("No Gemini API key found. Web search integration will not be available.")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo AI", description="AI-powered Todo List Application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Todo AI API"}

# Include routers
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["assistant"])
app.include_router(settings_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
