"""
Request Router for Todo AI

This module routes user requests to either the existing Todo AI agents
or specialized agents like the Gemini Web Agent based on the nature of the request.
"""

import logging
from typing import Dict, Any, Optional, List

# Import the specialized agents
from backend.agent.gemini_web_agent import GeminiWebAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestRouter:
    """
    Routes user requests to the appropriate agent system based on the request type.
    """

    def __init__(self, multi_agent_coordinator, gemini_api_key: Optional[str] = None):
        """
        Initialize the request router with the multi-agent coordinator and specialized agents.

        Args:
            multi_agent_coordinator: The existing Todo AI multi-agent coordinator
            gemini_api_key: Gemini API key for specialized agents (optional)
        """
        self.multi_agent_coordinator = multi_agent_coordinator
        self.web_search_agent = GeminiWebAgent(api_key=gemini_api_key)
        logger.info("Request router initialized with multi-agent system and specialized agents")

    def route_request(self, message: str, conversation_history: List[Dict[str, str]], user, db, assistant_mode=None) -> Dict[str, Any]:
        """
        Route a user request to the appropriate agent system.

        Args:
            message: The user's message/request
            conversation_history: The conversation history
            user: The user object
            db: Database session
            assistant_mode: The assistant mode to use (plan or act)

        Returns:
            Dict containing the response and any actions
        """
        # First, check if this is a web search query
        if self._is_web_search_query(message):
            logger.info(f"Routing web search query to WebSearchAgent: {message}")
            search_result = self.web_search_agent.process_query(message)

            if search_result.get("success", False):
                return {
                    "response": search_result["response"],
                    "source": "web_search",
                    "actions": []
                }
            else:
                # If web search failed, fall back to the multi-agent system
                logger.warning(f"Web search failed, falling back to multi-agent system: {search_result.get('error', 'Unknown error')}")

        # Use the existing Todo AI system for task management and other queries
        logger.info(f"Routing request to Todo AI multi-agent system: {message} in {assistant_mode} mode")
        response, actions = self.multi_agent_coordinator.process_message(
            message, conversation_history, user, db, assistant_mode
        )

        return {
            "response": response,
            "source": "todo_ai",
            "actions": actions
        }

    def _is_web_search_query(self, message: str) -> bool:
        """
        Determine if a message is a web search query.

        Args:
            message: The user's message

        Returns:
            Boolean indicating if the message is a web search query
        """
        # Use the WebSearchAgent's method to determine if this is a web search query
        return self.web_search_agent.is_web_search_query(message) if hasattr(self.web_search_agent, 'is_web_search_query') else False
