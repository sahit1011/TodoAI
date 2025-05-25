"""
Conversational Agent for Todo AI

This agent is responsible for:
1. Understanding user intent from natural language
2. Extracting relevant parameters for task operations
3. Providing natural language responses
4. Maintaining conversation context
"""

import json
import logging
import requests
import os
from typing import Dict, Any, Optional, List, Tuple

# Import documentation store
from backend.agent.multi_agent.documentation_store import DocumentationStore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API endpoint and key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDTRUomc-KVV_Ib2oaKHcxnMQGXKPRFLxE")

class ConversationalAgent:
    def __init__(self, model_name=None):
        """Initialize the conversational agent with the Gemini API."""
        try:
            self.api_url = GEMINI_API_URL
            self.api_key = GEMINI_API_KEY
            # Initialize the documentation store
            self.doc_store = DocumentationStore()
            logger.info("Conversational agent initialized with Gemini API")
        except Exception as e:
            logger.error(f"Error initializing conversational agent: {str(e)}")
            raise

    def process_message(self, message, conversation_history, user, db):
        """
        Process a user message and determine the intent and parameters.

        Args:
            message (str): The user's message
            conversation_history (list): Previous conversation turns
            user (User): The current user object
            db (Session): Database session

        Returns:
            dict: Contains intent, parameters, and natural language response
        """
        try:
            # Format conversation history for context
            formatted_history = self._format_conversation_history(conversation_history)

            # Prepare the prompt for the LLM
            prompt = self._create_prompt(message, formatted_history, user)

            # Prepare the request payload for Gemini API
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
                }
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
                logger.info(f"Raw LLM response: {response_text}")

                # Parse the response to extract intent, parameters, and response text
                parsed_response = self._parse_response(response_text)

                return parsed_response
            else:
                # Handle API error
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "intent": "conversation",
                    "parameters": {},
                    "response": f"I'm sorry, I encountered an error processing your request. {error_msg}"
                }
        except Exception as e:
            logger.error(f"Error in conversational agent: {str(e)}")
            return {
                "intent": "conversation",
                "parameters": {},
                "response": f"I'm sorry, I encountered an error processing your request. {str(e)}"
            }

    def _format_conversation_history(self, history):
        """Format the conversation history for inclusion in the prompt."""
        if not history:
            return "No previous conversation."

        formatted = []
        for turn in history[-5:]:  # Only include the last 5 turns to keep context manageable
            formatted.append(f"User: {turn['user']}")
            formatted.append(f"Assistant: {turn['assistant']}")

        return "\n".join(formatted)

    def _create_prompt(self, message, history, user):
        """Create a prompt for the LLM based on the user message and context."""

        # Determine if this might be a general question about the app
        relevant_sections = self.doc_store.get_relevant_sections(message)

        # Get relevant documentation if needed
        docs_context = ""
        if relevant_sections:
            docs_context = "# Relevant App Documentation\n" + self.doc_store.get_documentation(relevant_sections)
            logger.info(f"Including documentation sections: {', '.join(relevant_sections)}")

        # Create the note section for when no docs are included
        if not relevant_sections:
            # Check if this might be a general knowledge question
            general_knowledge_indicators = [
                "what is", "how does", "explain", "tell me about", "define", "meaning of",
                "why do", "why does", "what are", "how do", "what causes", "history of"
            ]

            is_general_knowledge = any(indicator in message.lower() for indicator in general_knowledge_indicators)

            if is_general_knowledge and not any(keyword in message.lower() for keyword in ["task", "todo", "priority", "due date", "app"]):
                note_section = "# Note\nThe user is asking a general knowledge question. Use your built-in knowledge to provide a helpful, informative response."
            else:
                note_section = "# Note\nThe user appears to be asking about task management rather than general app information."

        # Note: Web search is now handled by the specialized WebSearchAgent
        # This agent only handles task management and general knowledge questions

        return f"""
        You are an AI assistant for a todo application. The user has said: "{message}"

        Based on their message, determine what they want to do with their tasks or if they're asking a general question about the app.

        Previous conversation:
        {history}

        {docs_context if docs_context else note_section}

        Analyze the user's message and respond with a JSON object containing:
        1. "intent": One of ["task_create", "task_update", "task_delete", "task_list", "task_complete", "task_reopen", "conversation"]
        2. "parameters": An object containing relevant parameters for the action (e.g., task title, priority, status, etc.)
        3. "response": A natural language response to the user

        For task_create, include "title" and optionally "priority" (high, medium, low) and "due_date".
        For task_update, include "task_id" and the fields to update.
        For task_delete, include "task_id" or "task_title". If the user doesn't specify which task to delete, ask them to provide more details.
        For task_list, include optional filters like "status" or "priority".
        When the user asks for "active tasks", "pending tasks", or "incomplete tasks", set intent to "task_list" with parameter "status": "todo".
        For task_complete or task_reopen, include "task_id" or "task_title".

        IMPORTANT: If the user is asking a general question about the app's capabilities, features, concepts (like what "priority" means), or how to use the app, set intent to "conversation" and provide a helpful response using the information from the App Documentation section above.

        CRITICAL: If the user asks you to perform actions that are outside the scope of task management, such as:
        - Sending emails, messages, or communicating with external services
        - Making phone calls or contacting people
        - Accessing the internet or searching the web in real-time
        - Performing actions outside of task management
        - Accessing or modifying files on their computer
        - Scheduling meetings or managing their calendar

        You MUST set intent to "conversation" and explain that you cannot perform these actions because they are outside the scope of the Todo AI app. DO NOT set intent to task_create or any other task-related intent for these requests. Refer to the limitations documentation for guidance.

        IMPORTANT: You CAN and SHOULD answer general knowledge questions using your built-in knowledge. For example, if a user asks "What is an ECG?" or "How does photosynthesis work?", you should provide a helpful, informative response based on your training data. You don't need to access the internet for this - use what you already know. Set the intent to "conversation" for these types of questions.

        IMPORTANT: For questions about current events, weather, or other real-time information that require web search, simply set the intent to "conversation" and explain that you'll need to use the web search functionality to answer this question accurately. The system will automatically route these queries to a specialized web search agent.

        When answering general questions about the app:
        1. Be thorough and informative, using the documentation as your primary source
        2. If the user is asking about a specific concept (like "priority"), provide a detailed explanation
        3. Include examples of relevant commands when appropriate
        4. Keep your response conversational and user-friendly
        5. Don't list tasks unless the user specifically asks to see their tasks

        If the user is just having a conversation (greeting, asking how you are, etc.), set intent to "conversation".

        IMPORTANT: Before setting any task-related intent (task_create, task_update, etc.), carefully check if the user's request is actually about managing tasks within the app. If there's any doubt, set intent to "conversation" and ask for clarification.

        IMPORTANT: When the user refers to a task by title, you should be flexible and try to match the closest task title.
        For example, if the user says "delete schedule team meeting task" and there's a task with title "Schedule team meeting",
        you should understand they're referring to the same task and include "task_title": "Schedule team meeting" in your parameters.

        Be flexible with capitalization, word order, and partial matches. If there's ambiguity, include a confirmation
        in your response asking the user to confirm which task they meant.

        If you can find the task ID from the conversation history, include it as "task_id". Otherwise, include the best matching
        "task_title" you can find.

        IMPORTANT: When the user asks about tasks with specific keywords (e.g., "tasks about mom"), DO NOT make specific claims
        about which tasks exist or their details. Instead, set the intent to "task_list" with a "query" parameter containing
        the search terms, and let the action agent find and report the actual matching tasks. Your response should be phrased
        as "Let me check for tasks related to [topic]" rather than claiming specific tasks exist.

        IMPORTANT: When the user asks to complete, update, or delete a task, DO NOT claim in your response that the action
        has already been completed successfully. Instead, phrase your response as "I'll mark that task as complete" or
        "I'll try to update that task" rather than "I've marked the task as complete" or "I've updated the task".
        The action agent will determine if the task exists and can be modified, and will provide the actual confirmation.

        For task_complete, task_update, and task_delete intents, your response should indicate that you will attempt the action,
        not that you have already done it. For example:
        - "I'll mark that task as complete for you."
        - "I'll try to update that task with the new information."
        - "I'll delete that task for you."

        NEVER use phrases like "Great! I've marked..." or "I've completed..." or "I've updated..." as these imply the action
        has already been done successfully. Always use future tense like "I'll try to..." or "I'll mark..." instead.

        IMPORTANT: When you need more information from the user to complete an action, make sure to:
        1. Include a question mark (?) in your response
        2. Be very explicit about what information you need
        3. Set the appropriate intent (e.g., task_update, task_create) even when asking for more information

        For example, if the user says "change the priority of my homework task" but doesn't specify the new priority:
        - DO: "I'll update your homework task. What priority would you like to set it to (high, medium, or low)?"
        - DON'T: "I'll update your homework task with the new priority."

        If the user says "create a new task" without providing details:
        - DO: "I'll create a new task for you. What would you like to title this task?"
        - DON'T: "I'll create a new task."

        Respond ONLY with a valid JSON object.
        """

    def _parse_response(self, response):
        """Parse the LLM response to extract structured data."""
        try:
            # Try to extract JSON from the response
            # First, look for JSON-like structure
            response = response.strip()

            # If the response is wrapped in ```json and ```, extract just the JSON part
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            parsed = json.loads(response)

            # Ensure the required fields are present
            if "intent" not in parsed:
                parsed["intent"] = "conversation"
            if "parameters" not in parsed:
                parsed["parameters"] = {}
            if "response" not in parsed:
                parsed["response"] = "I'm not sure how to respond to that."

            return parsed
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Fallback to conversation intent if parsing fails
            return {
                "intent": "conversation",
                "parameters": {},
                "response": "I'm sorry, I couldn't understand your request. Could you please rephrase it?"
            }
