"""
Multi-Agent Process Interface

This module provides the main interface for the multi-agent system.
It initializes the system and processes messages from users.

The multi-agent system consists of:
1. A conversational agent that understands user intent from natural language
2. An action agent that executes database operations based on user intent
3. A coordinator that manages the flow of information between the agents

The system uses the Gemini API for both agents, with different prompts to make them behave as separate agents.
The conversational agent extracts intent and parameters from user messages, and the action agent performs
the corresponding database operations.

Example usage:
    response, actions = multi_agent_process(message, conversation_context, user, db)

    # response is a natural language response to the user
    # actions is a list of actions for the frontend to perform
"""

import logging
import os
from .multi_agent import MultiAgentCoordinator

# Import the request router for specialized agents
try:
    from .langchain_integration.request_router import RequestRouter
    from .gemini_web_agent import GeminiWebAgent
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    WEB_SEARCH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Specialized agents not available: {str(e)}. Will use only the Todo AI system.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the multi-agent system
try:
    multi_agent = MultiAgentCoordinator()
    logger.info("Multi-agent system initialized successfully")

    # Initialize the request router if web search is available
    if WEB_SEARCH_AVAILABLE:
        try:
            # Get Gemini API key from environment variable
            gemini_api_key = os.environ.get("GEMINI_API_KEY")
            request_router = RequestRouter(multi_agent, gemini_api_key)
            logger.info("Request router initialized with web search integration")
        except Exception as e:
            logger.error(f"Failed to initialize request router: {str(e)}")
            request_router = None
    else:
        request_router = None
except Exception as e:
    logger.error(f"Failed to initialize multi-agent system: {str(e)}")
    multi_agent = None
    request_router = None

def multi_agent_process(message, conversation_context, user, db, assistant_mode=None):
    """
    Process a message using the multi-agent system.

    Args:
        message (str): The user's message
        conversation_context (list): Previous conversation turns
        user (User): The current user object
        db (Session): Database session
        assistant_mode (str, optional): The assistant mode to use. If None, uses the user's preferred mode.

    Returns:
        tuple: (response_text, actions)
    """
    try:
        if multi_agent is None:
            raise RuntimeError("Multi-agent system is not initialized")

        # Log the incoming message
        logger.info(f"Processing message in multi_agent_process: {message}")

        # Check if we should use the specialized agents for certain requests
        if request_router is not None and WEB_SEARCH_AVAILABLE:
            # Use the router to determine which system should handle the request
            result = request_router.route_request(message, conversation_context, user, db, assistant_mode)

            # Process the result based on its source
            if isinstance(result, dict) and "source" in result:
                if result["source"] == "web_search":
                    # Result from the web search agent
                    response = result["response"]
                    actions = result.get("actions", [])
                    logger.info(f"Response from WebSearchAgent: {response[:100]}...")
                elif result["source"] == "todo_ai":
                    # Result from the Todo AI system
                    response = result["response"]
                    actions = result.get("actions", [])
                    logger.info(f"Response from Todo AI coordinator: {response[:100]}...")
                else:
                    # Unknown source
                    response = result["response"]
                    actions = result.get("actions", [])
                    logger.info(f"Response from unknown source: {response[:100]}...")
            else:
                # Legacy format handling for backward compatibility
                response, actions = result
                logger.info(f"Response from legacy format: {response[:100]}...")

            # Extract UI actions from the actions list
            ui_actions = []
            for action in actions:
                if isinstance(action, dict) and "uiActions" in action:
                    ui_actions = action["uiActions"]
                    # Add the UI actions as a separate action
                    actions.append({"type": "ui_actions", "uiActions": ui_actions})
                    break

            # Debug the actions and UI actions
            logger.info(f"Actions after extraction: {actions}")
            logger.info(f"UI actions after extraction: {ui_actions}")
        else:
            # Use only the Todo AI system with the specified mode
            response, actions = multi_agent.process_message(
                message, conversation_context, user, db, assistant_mode
            )
            logger.info(f"Response from coordinator in {assistant_mode} mode: {response[:100]}...")

            # Extract UI actions from the actions list
            ui_actions = []
            for action in actions:
                if isinstance(action, dict) and "uiActions" in action:
                    ui_actions = action["uiActions"]
                    # UI actions are already included in the actions list
                    break

            # Debug the actions and UI actions
            logger.info(f"Actions after extraction: {actions}")
            logger.info(f"UI actions after extraction: {ui_actions}")

        # Update conversation context
        conversation_context.append({
            "user": message,
            "assistant": response
        })

        # Trim conversation context if it gets too long
        if len(conversation_context) > 20:
            conversation_context = conversation_context[-20:]

        return response, actions
    except Exception as e:
        logger.error(f"Error in multi_agent_process: {str(e)}")

        # Create a user-friendly error message
        error_message = str(e)
        logger.info(f"Creating user-friendly error message for: {error_message}")

        if "not found" in error_message.lower() and "Task with title" in error_message:
            # Extract the task title from the error message
            task_title = error_message.split("Task with title")[1].split("not found")[0].strip().replace("'", "")
            error_response = f"I couldn't find a task matching '{task_title}'. Please check the task name or create this task first."
        elif "not found" in error_message.lower() and "Task with ID" in error_message:
            # Extract the task ID from the error message
            task_id = error_message.split("Task with ID")[1].split("not found")[0].strip()
            error_response = f"I couldn't find a task with ID {task_id}. Please check the ID and try again."
        else:
            # For other errors, don't expose the technical details
            error_response = "I'm sorry, I encountered an issue while processing your request. Please try again or rephrase your request."

        logger.info(f"User-friendly error response: {error_response}")

        # Update conversation context even on error
        conversation_context.append({
            "user": message,
            "assistant": error_response
        })

        return error_response, []
