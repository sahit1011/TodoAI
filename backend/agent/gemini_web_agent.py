"""
Gemini Web Search Agent for Todo AI

This agent uses Google's Gemini model with its built-in web search capabilities
to answer questions that require real-time information from the web.
"""

import logging
import os
import json
import requests
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiWebAgent:
    """
    Agent that uses Gemini's built-in web search capabilities to answer questions.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini web search agent.

        Args:
            api_key: Gemini API key (optional, will use environment variable if not provided)
        """
        # Set API key
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("No Gemini API key provided. Web search agent will not function properly.")
            self.agent_initialized = False
            return

        # Initialize Gemini API URL - using the model with web search capabilities
        # Note: Using the latest model that has web search capabilities
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

        self.agent_initialized = True
        logger.info("Gemini web search agent initialized successfully")

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a web search query using Gemini's built-in web search capabilities.

        Args:
            query: The user's search query

        Returns:
            Dict containing the response and metadata
        """
        if not self.agent_initialized:
            return {
                "response": "I'm sorry, but I'm currently unable to search the web due to configuration issues. Please try again later.",
                "success": False
            }

        try:
            logger.info(f"Processing web search query with Gemini: {query}")

            # Create a prompt that explicitly asks Gemini to search the web
            prompt = f"""
            Please search the web to answer this question: {query}

            Provide a comprehensive and accurate response based on current information from the web.
            Include relevant facts, figures, and information.
            Cite your sources at the end of your response.
            If the information might be outdated, acknowledge that limitation.
            """

            # Call the Gemini API with web search enabled
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 1024
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ],
                # Enable web search for this query
                "tools": [
                    {
                        "googleSearchRetrieval": {}
                    }
                ]
            }

            # Call the Gemini API
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Extract the response text
                response_data = response.json()
                response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Gemini web search response generated")

                return {
                    "response": response_text,
                    "success": True,
                    "source": "gemini_web_search"
                }
            else:
                # Handle API error
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "response": "I encountered an issue while searching the web. Please try again later.",
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            logger.error(f"Error in Gemini web search agent: {str(e)}")
            return {
                "response": "I encountered an issue while searching for information. Please try a different query or try again later.",
                "success": False,
                "error": str(e)
            }

    def is_web_search_query(self, message: str) -> bool:
        """
        Determine if a message is a web search query.

        Args:
            message: The user's message

        Returns:
            Boolean indicating if the message is a web search query
        """
        # Define patterns that indicate web search queries
        web_search_keywords = [
            "search for", "look up", "find information about", "search the web",
            "what is the current", "latest news", "recent events", "weather in",
            "what's happening", "news about", "current status of", "updates on",
            "stock price", "market update", "sports scores", "game results",
            "trending", "viral", "breaking news", "current events"
        ]

        # Check if any keyword is in the message
        return any(keyword in message.lower() for keyword in web_search_keywords)


# For testing
if __name__ == "__main__":
    # Test the Gemini web search agent
    agent = GeminiWebAgent()
    response = agent.process_query("What is the current weather in New York?")
    print(json.dumps(response, indent=2))
