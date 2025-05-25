"""
Configuration module for Todo AI

This module loads environment variables and provides configuration settings
for the application.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"No .env file found at {env_path}. Using system environment variables.")

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Check if required API keys are available
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found. LangChain integration will be limited.")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found. Todo AI functionality will be limited.")

# Application settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# UI-first mode: When enabled, tasks are only added after UI actions are completed
# This is used for demonstration purposes to show the AI interacting with the UI
UI_FIRST_MODE = os.environ.get("UI_FIRST_MODE", "True").lower() == "true"

# Assistant mode settings
# PLAN_MODE: Direct API calls without UI interaction
# ACT_MODE: Visual UI automation where the AI mimics user interactions
ASSISTANT_MODES = {
    "PLAN": "plan",
    "ACT": "act"
}
DEFAULT_ASSISTANT_MODE = os.environ.get("DEFAULT_ASSISTANT_MODE", ASSISTANT_MODES["ACT"])

# Assistant mode settings
# PLAN_MODE: Direct API calls without UI interaction
# ACT_MODE: Visual UI automation where the AI mimics user interactions
ASSISTANT_MODES = {
    "PLAN": "plan",
    "ACT": "act"
}
DEFAULT_ASSISTANT_MODE = os.environ.get("DEFAULT_ASSISTANT_MODE", ASSISTANT_MODES["ACT"])

# Set log level based on configuration
logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))

# Export configuration
config = {
    "api_keys": {
        "openai": OPENAI_API_KEY,
        "serpapi": SERPAPI_API_KEY,
        "gemini": GEMINI_API_KEY
    },
    "debug": DEBUG,
    "log_level": LOG_LEVEL,
    "ui_first_mode": UI_FIRST_MODE,
    "assistant_modes": ASSISTANT_MODES,
    "default_assistant_mode": DEFAULT_ASSISTANT_MODE
}

def get_config():
    """Get the application configuration."""
    return config
