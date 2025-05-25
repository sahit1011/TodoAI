"""
Web search functionality for the Todo AI assistant.
"""

import logging
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_web(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo and return the results.

    Args:
        query: The search query
        num_results: Number of results to return (default: 3)

    Returns:
        List of search results, each containing title, link, and snippet
    """
    try:
        logger.info(f"Searching the web for: {query}")

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))

        logger.info(f"Found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error searching the web: {str(e)}")
        # Return mock results for demonstration purposes when rate limited
        if "Ratelimit" in str(e):
            logger.info("Using mock results due to rate limiting")
            return [
                {
                    "title": "Mock Search Result 1",
                    "body": "This is a mock search result because we've been rate limited by DuckDuckGo. In a production environment, we would implement proper rate limiting and fallback mechanisms.",
                    "href": "https://example.com/mock1"
                },
                {
                    "title": "Mock Search Result 2",
                    "body": "This is another mock search result. In a real application, we might use multiple search providers or implement caching to avoid rate limits.",
                    "href": "https://example.com/mock2"
                }
            ]
        return []

def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results into a readable string.

    Args:
        results: List of search results from search_web()

    Returns:
        Formatted string with search results
    """
    if not results:
        return "No search results found."

    formatted = "IMPORTANT - REAL-TIME WEB SEARCH RESULTS:\n\n"

    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        body = result.get('body', 'No content')
        href = result.get('href', 'No link')

        formatted += f"{i}. **{title}**\n"
        formatted += f"{body}\n"
        formatted += f"Source: {href}\n\n"

    formatted += "\nUSE THE ABOVE REAL-TIME INFORMATION TO ANSWER THE USER'S QUESTION. DO NOT CLAIM YOU DON'T HAVE ACCESS TO REAL-TIME INFORMATION.\n"

    return formatted
