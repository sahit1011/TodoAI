"""
LangChain Agent Integration for Todo AI

This module provides integration with LangChain for handling out-of-scope requests
like web searches, real-time data access, and other external services.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional

# LangChain imports
from langchain_community.agents import Tool, initialize_agent, AgentType
import google.generativeai as genai
from langchain_core.language_models.llms import BaseLLM
from langchain_community.tools import DuckDuckGoSearchRun

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangChainAgent:
    """
    LangChain agent for handling out-of-scope requests in Todo AI.
    This agent is activated only when users request functionality beyond
    the core task management capabilities.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LangChain agent with necessary tools and models.

        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        # Set API key
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("No Gemini API key provided. LangChain agent will not function properly.")

        # Initialize Gemini
        genai.configure(api_key=self.api_key)

        # Create a custom LLM class for Gemini
        class GeminiLLM(BaseLLM):
            def _call(self, prompt, stop=None):
                response = genai.GenerativeModel("models/gemini-1.5-pro-latest").generate_content(prompt)
                return response.text

            @property
            def _llm_type(self):
                return "gemini"

        # Initialize LLM
        self.llm = GeminiLLM()

        # Initialize tools
        self.tools = self._initialize_tools()

        # Initialize agent
        self.agent = self._initialize_agent()

        logger.info("LangChain agent initialized successfully")

    def _initialize_tools(self) -> List[Tool]:
        """Initialize and return a list of tools for the agent to use."""
        tools = [
            Tool(
                name="WebSearch",
                func=DuckDuckGoSearchRun().run,
                description="Useful for searching the web for current information. Use this when you need to find information about current events, facts, or anything that requires up-to-date information."
            )
        ]
        return tools

    def _initialize_agent(self):
        """Initialize and return the LangChain agent."""
        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def process_request(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user request using the LangChain agent.

        Args:
            user_message: The user's message/request

        Returns:
            Dict containing the response and any actions
        """
        try:
            logger.info(f"Processing out-of-scope request with LangChain: {user_message}")

            # Run the agent
            response = self.agent.run(user_message)

            logger.info(f"LangChain agent response: {response}")

            return {
                "response": response,
                "source": "langchain",
                "actions": []  # No UI actions for LangChain responses
            }
        except Exception as e:
            logger.error(f"Error in LangChain agent: {str(e)}")
            return {
                "response": f"I encountered an issue while trying to process your request. Please try again or ask something else.",
                "source": "langchain_error",
                "actions": []
            }

    def is_request_supported(self, user_message: str) -> bool:
        """
        Determine if a user request is supported by the LangChain agent.

        Args:
            user_message: The user's message/request

        Returns:
            Boolean indicating if the request is supported
        """
        # Define patterns that indicate out-of-scope requests
        out_of_scope_indicators = [
            "search", "look up", "find information", "what is", "how does",
            "current", "latest", "news", "weather", "stock", "price",
            "who is", "where is", "when did", "why does", "explain",
            "calculate", "convert", "translate"
        ]

        # Check if any indicator is in the message
        return any(indicator in user_message.lower() for indicator in out_of_scope_indicators)


# For testing
if __name__ == "__main__":
    # Test the LangChain agent
    agent = LangChainAgent()
    response = agent.process_request("What is the capital of France?")
    print(json.dumps(response, indent=2))
