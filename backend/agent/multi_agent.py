import os
import json
import requests
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.models.user import User
from backend.models.task import Task
from backend.agent.simple_gemini import process_message as task_agent_process

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Gemini assistant will not work.")

# Gemini API endpoint for Gemini 2.5 Pro Experimental (free tier)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent"

def process_message(
    message: str,
    conversation_context: List[Dict[str, str]],
    user: User,
    db: Session
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Multi-agent message processor that routes messages to the appropriate agent.

    Args:
        message: The user's message
        conversation_context: The conversation history
        user: The current user
        db: Database session

    Returns:
        Tuple of (response_text, actions)
    """
    # Add user message to context
    conversation_context.append({"role": "user", "content": message})

    try:
        # First, determine the message type using the router agent
        message_type, confidence = router_agent(message, conversation_context)

        # Route to the appropriate agent based on message type
        if message_type == "task" and confidence > 0.6:
            # Use the existing task agent for task-related queries
            response, actions = task_agent_process(message, conversation_context, user, db)
        else:
            # Use the general conversation agent for everything else
            response, actions = conversation_agent(message, conversation_context, user, db)

        # Add assistant response to context
        conversation_context.append({"role": "assistant", "content": response})

        return response, actions
    except Exception as e:
        print(f"Error in multi-agent system: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again.", []

def router_agent(message: str, conversation_context: List[Dict[str, str]]) -> Tuple[str, float]:
    """
    Determines the type of message and routes it to the appropriate agent.

    Args:
        message: The user's message
        conversation_context: The conversation history

    Returns:
        Tuple of (message_type, confidence)
    """
    if not GEMINI_API_KEY:
        print("Error in router agent: GEMINI_API_KEY not found")
        return "general", 0.0

    try:
        # Create system prompt
        system_prompt = """
        You are a message router for a todo app assistant. Your job is to determine if the user's message is related to task management or general conversation.

        Task management includes:
        - Creating tasks
        - Updating tasks
        - Deleting tasks
        - Listing tasks
        - Marking tasks as complete
        - Getting task details
        - Setting reminders
        - Changing task priorities
        - Searching for tasks

        General conversation includes:
        - Greetings and small talk
        - Questions about the app's functionality
        - Help requests not specific to tasks
        - Any other non-task related queries

        Respond with a JSON object containing:
        1. "type": Either "task" or "general"
        2. "confidence": A number between 0 and 1 indicating how confident you are in this classification

        Examples:
        - "Add a task to call John tomorrow" -> {"type": "task", "confidence": 0.95}
        - "Hi, how are you today?" -> {"type": "general", "confidence": 0.9}
        - "What can this app do?" -> {"type": "general", "confidence": 0.8}
        - "Show me my high priority tasks" -> {"type": "task", "confidence": 0.9}
        """

        # Get the last few messages for context (up to 5)
        recent_context = conversation_context[-5:] if len(conversation_context) > 5 else conversation_context
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_context])

        # Prepare request payload for Gemini 2.5 Pro Preview
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\nConversation context:\n{context_text}\n\nUser message: {message}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 256
            }
        }

        # Make API request
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            response_data = response.json()

            # Extract text from response for Gemini 2.5 Pro Preview
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                if 'content' in response_data['candidates'][0]:
                    content = response_data['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        text = content['parts'][0]['text']
                    else:
                        text = ''
                else:
                    text = ''

                # Find JSON object in the response
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx]
                    try:
                        result = json.loads(json_str)

                        message_type = result.get("type", "general")
                        confidence = result.get("confidence", 0.5)

                        return message_type, confidence
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON from response: {json_str}")

            print(f"Error parsing router agent response: No valid JSON found")
            return "general", 0.5
        else:
            print(f"Error from router agent: {response.status_code} - {response.text}")
            return "general", 0.5

    except Exception as e:
        print(f"Error in router agent: {e}")
        return "general", 0.5

def conversation_agent(
    message: str,
    conversation_context: List[Dict[str, str]],
    user: User,
    db: Session
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Handles general conversation and app information queries.

    Args:
        message: The user's message
        conversation_context: The conversation history
        user: The current user
        db: Database session

    Returns:
        Tuple of (response_text, actions)
    """
    if not GEMINI_API_KEY:
        print("Error in conversation agent: GEMINI_API_KEY not found")
        return "I'm sorry, I'm having trouble accessing my knowledge base right now. Please try again later.", []

    try:
        # Get user's task statistics
        task_count = db.query(Task).filter(Task.user_id == user.id).count()
        completed_count = db.query(Task).filter(Task.user_id == user.id, Task.status == "done").count()
        high_priority_count = db.query(Task).filter(Task.user_id == user.id, Task.priority.in_(["high", "urgent"])).count()

        # Create system prompt with app information and user stats
        system_prompt = f"""
        You are an AI assistant for a Todo AI application. You can help users manage their tasks and answer questions about the app.

        About the Todo AI app:
        - Todo AI is a task management application with an AI assistant (that's you!)
        - Users can create, view, update, and delete tasks through both the UI and by talking to you
        - Tasks have properties like title, description, priority, and status
        - You can help users manage their tasks through natural language
        - The app has both traditional UI controls and an AI-powered interface

        Current user statistics:
        - Total tasks: {task_count}
        - Completed tasks: {completed_count}
        - High priority tasks: {high_priority_count}

        App features:
        1. Task Management:
           - Create tasks with title, description, and priority
           - View all tasks or filter by status
           - Update task details
           - Mark tasks as complete
           - Delete tasks

        2. AI Assistant (you):
           - Control the app through natural language
           - Create, update, and delete tasks through conversation
           - Get information about tasks
           - Answer questions about the app

        Be helpful, friendly, and conversational. If the user asks about task management, suggest they can either use the UI controls or ask you to help them with specific tasks.

        If the user seems to be trying to create, update, or manage tasks but you're not sure, suggest specific task-related commands they could try.
        """

        # Get the last few messages for context (up to 5)
        recent_context = conversation_context[-5:] if len(conversation_context) > 5 else conversation_context
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_context])

        # Prepare request payload for Gemini 2.5 Pro Preview
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\nConversation context:\n{context_text}\n\nUser message: {message}\n\nRespond in a helpful, friendly, and conversational way:"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }

        # Make API request
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Check if request was successful
        if response.status_code == 200:
            response_data = response.json()

            # Extract text from response for Gemini 2.5 Pro Preview
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                if 'content' in response_data['candidates'][0]:
                    content = response_data['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        text = content['parts'][0]['text']
                        return text, []

            # If we couldn't extract text from the response
            print(f"Error parsing conversation agent response: {response_data}")

            print(f"Error parsing conversation agent response")
            return "I'm sorry, I'm having trouble formulating a response right now. How else can I help you?", []
        else:
            print(f"Error from conversation agent: {response.status_code} - {response.text}")
            return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later.", []

    except Exception as e:
        print(f"Error in conversation agent: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again.", []
