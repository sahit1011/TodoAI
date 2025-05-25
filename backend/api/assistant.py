from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.database import get_db
from backend.auth import get_current_active_user
from backend.models.user import User
from backend.schemas import ChatMessage, ChatResponse, ChatResponseWithUIActions
from backend.config import ASSISTANT_MODES

# Import assistants
from backend.agent.assistant import process_message as openai_process_message
from backend.agent.simple_gemini import process_message as gemini_process_message
from backend.agent.multi_agent_process import multi_agent_process

router = APIRouter()

# Store conversation context for each user
conversation_contexts: Dict[str, Any] = {}

@router.post("/chat", response_model=ChatResponseWithUIActions)
async def chat_with_assistant(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get or initialize conversation context for the user
    user_id = str(current_user.id)
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = []

    # Get the assistant mode from the request or use the user's preferred mode
    assistant_mode = message.assistant_mode
    if not assistant_mode:
        assistant_mode = current_user.preferred_assistant_mode
        logger.info(f"Using user's preferred assistant mode: {assistant_mode}")
    else:
        logger.info(f"Using specified assistant mode: {assistant_mode}")

    # Use multi-agent system with the specified mode
    response, actions = multi_agent_process(
        message.message,
        conversation_contexts[user_id],
        current_user,
        db,
        assistant_mode
    )

    # Extract UI actions if present
    ui_actions = []
    for action in actions:
        if isinstance(action, dict) and "uiActions" in action:
            ui_actions = action["uiActions"]
            logger.info(f"Found UI actions in response: {ui_actions}")
            break

    # Debug the response
    logger.info(f"Returning response with UI actions: {ui_actions}")

    return ChatResponseWithUIActions(response=response, actions=actions, uiActions=ui_actions)

@router.post("/reset", response_model=ChatResponse)
async def reset_conversation(
    current_user: User = Depends(get_current_active_user)
):
    # Reset the conversation context for the user
    user_id = str(current_user.id)
    conversation_contexts[user_id] = []

    return ChatResponse(
        response="Conversation has been reset. How can I help you with your tasks today?",
        actions=None
    )
