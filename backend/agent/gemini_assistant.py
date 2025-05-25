import os
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from dotenv import load_dotenv
import json

from backend.models.user import User
from backend.models.task import Task, PriorityEnum, StatusEnum

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Gemini assistant will not work.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Define intents (same as in the original assistant)
INTENTS = {
    "add_task": "Create a new task",
    "update_task": "Update an existing task",
    "delete_task": "Delete a task",
    "list_tasks": "List all tasks or filtered tasks",
    "mark_complete": "Mark a task as complete",
    "get_task_details": "Get details about a specific task",
    "set_reminder": "Set a reminder for a task",
    "change_priority": "Change the priority of a task",
    "assign_task": "Assign a task to someone",
    "search_tasks": "Search for tasks",
    "help": "Get help with using the assistant",
    "unknown": "Unknown intent"
}

def process_message(
    message: str,
    conversation_context: List[Dict[str, str]],
    user: User,
    db: Session
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Process a user message and return a response and actions.

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
        # Classify intent
        intent, parameters = classify_intent(message, conversation_context)

        # Execute action based on intent
        response, actions = execute_action(intent, parameters, user, db, conversation_context)

        # Add assistant response to context
        conversation_context.append({"role": "assistant", "content": response})

        return response, actions
    except Exception as e:
        print(f"Error processing message: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again.", []

def classify_intent(message: str, conversation_context: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
    """
    Classify the intent of a user message and extract parameters.

    Args:
        message: The user's message
        conversation_context: The conversation history

    Returns:
        Tuple of (intent, parameters)
    """
    if not GEMINI_API_KEY:
        print("Error classifying intent: GEMINI_API_KEY not found")
        return "unknown", {}

    try:
        # Create system prompt
        system_prompt = """
        You are an AI assistant for a todo list application. Your task is to classify the user's intent and extract parameters.

        Respond with a JSON object containing:
        1. "intent": One of the following intents:
            - add_task: Create a new task
            - update_task: Update an existing task
            - delete_task: Delete a task
            - list_tasks: List all tasks or filtered tasks
            - mark_complete: Mark a task as complete
            - get_task_details: Get details about a specific task
            - set_reminder: Set a reminder for a task
            - change_priority: Change the priority of a task
            - assign_task: Assign a task to someone
            - search_tasks: Search for tasks
            - help: Get help with using the assistant
            - unknown: If the intent doesn't match any of the above

        2. "parameters": An object containing parameters for the intent, such as:
            - title: The title of a task
            - description: The description of a task
            - task_id: The ID of a task (if mentioned by number or position)
            - due_date: The due date of a task
            - priority: The priority of a task (low, medium, high, urgent)
            - status: The status of a task (todo, in_progress, done, archived)
            - query: Search query for tasks
            - filter: Filter for listing tasks (e.g., "completed", "high priority")

        For dates, convert to ISO format (YYYY-MM-DD).
        For priorities, use: low, medium, high, urgent
        For status, use: todo, in_progress, done, archived

        Only include parameters that are explicitly mentioned or can be clearly inferred from the message.
       use gemini only
         """

        # Format conversation history for Gemini
        gemini_messages = [
            {"role": "user", "parts": [system_prompt + "\n\nUser message: " + message]}
        ]

        # Call Gemini API
        try:
            # Use the older API format since we're using version 0.1.0rc2
            response = genai.generate_text(
                model='models/text-bison-001',  # Use a supported model for older API
                prompt=gemini_messages[0]['parts'][0],
                temperature=0.1
            )

            # Parse the response
            # Try to extract JSON from the response
            if hasattr(response, 'text'):
                # New API format
                content = response.text
            else:
                # Old API format
                content = response.result

            # Find JSON object in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)

                intent = result.get("intent", "unknown")
                parameters = result.get("parameters", {})

                return intent, parameters
            else:
                print(f"Error parsing Gemini response: No JSON found in: {content}")
                return "unknown", {}
        except Exception as e:
            print(f"Error parsing Gemini response: {e}, Response: {str(response)}")
            return "unknown", {}

    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "unknown", {}

def execute_action(
    intent: str,
    parameters: Dict[str, Any],
    user: User,
    db: Session,
    conversation_context: List[Dict[str, str]]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Execute an action based on the intent and parameters.

    Args:
        intent: The classified intent
        parameters: The extracted parameters
        user: The current user
        db: Database session
        conversation_context: The conversation history

    Returns:
        Tuple of (response_text, actions)
    """
    # Handle different intents
    if intent == "add_task":
        return handle_add_task(parameters, user, db)
    elif intent == "list_tasks":
        return handle_list_tasks(parameters, user, db)
    elif intent == "mark_complete":
        return handle_mark_complete(parameters, user, db)
    elif intent == "update_task":
        return handle_update_task(parameters, user, db)
    elif intent == "delete_task":
        return handle_delete_task(parameters, user, db)
    elif intent == "get_task_details":
        return handle_get_task_details(parameters, user, db)
    elif intent == "change_priority":
        return handle_change_priority(parameters, user, db)
    elif intent == "help":
        return handle_help()
    else:
        return "I'm not sure what you want to do. Can you please be more specific?", []

def handle_add_task(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle adding a new task."""
    title = parameters.get("title")
    if not title:
        return "I need a title for the task. What would you like to call it?", []

    # Create new task
    new_task = Task(
        title=title,
        description=parameters.get("description"),
        due_date=parameters.get("due_date"),
        priority=parameters.get("priority", "medium"),
        status=parameters.get("status", "todo"),
        user_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    response = f"I've added a new task: '{title}'"
    if new_task.description:
        response += f" with description: '{new_task.description}'"
    if new_task.due_date:
        response += f", due on {new_task.due_date.strftime('%Y-%m-%d')}"
    if new_task.priority:
        response += f", priority: {new_task.priority}"

    return response, [{"type": "task_added", "task_id": new_task.id}]

def handle_list_tasks(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle listing tasks."""
    # Query tasks
    query = db.query(Task).filter(Task.user_id == user.id)

    # Apply filters
    filter_type = parameters.get("filter", "").lower()
    if filter_type == "completed" or filter_type == "done":
        query = query.filter(Task.status == "done")
    elif filter_type == "active" or filter_type == "todo":
        query = query.filter(Task.status == "todo")
    elif filter_type == "high priority" or filter_type == "high":
        query = query.filter(Task.priority == "high")
    elif filter_type == "urgent":
        query = query.filter(Task.priority == "urgent")

    tasks = query.all()

    if not tasks:
        return "You don't have any tasks that match your criteria.", []

    # Format response
    response = f"Here are your tasks ({len(tasks)} total):\n\n"
    for i, task in enumerate(tasks, 1):
        status_emoji = "✅" if task.status == "done" else "⏳"
        priority_emoji = "🔴" if task.priority == "high" or task.priority == "urgent" else "🟡" if task.priority == "medium" else "🟢"

        response += f"{i}. {status_emoji} {priority_emoji} {task.title}"
        if task.due_date:
            response += f" (Due: {task.due_date.strftime('%Y-%m-%d')})"
        response += "\n"

    return response, [{"type": "tasks_listed", "count": len(tasks)}]

def handle_mark_complete(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle marking a task as complete."""
    task_id = parameters.get("task_id")
    title = parameters.get("title")

    if not task_id and not title:
        return "Which task would you like to mark as complete?", []

    # Find the task
    query = db.query(Task).filter(Task.user_id == user.id)
    if task_id:
        task = query.filter(Task.id == task_id).first()
    else:
        # Try to find by title (partial match)
        task = query.filter(Task.title.ilike(f"%{title}%")).first()

    if not task:
        return "I couldn't find that task. Could you try again with a different task?", []

    # Update task status
    task.status = "done"
    db.commit()

    return f"I've marked '{task.title}' as complete.", [{"type": "task_updated", "task_id": task.id}]

def handle_update_task(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle updating a task."""
    task_id = parameters.get("task_id")
    title = parameters.get("title")

    if not task_id and not title:
        return "Which task would you like to update?", []

    # Find the task
    query = db.query(Task).filter(Task.user_id == user.id)
    if task_id:
        task = query.filter(Task.id == task_id).first()
    else:
        # Try to find by title (partial match)
        task = query.filter(Task.title.ilike(f"%{title}%")).first()

    if not task:
        return "I couldn't find that task. Could you try again with a different task?", []

    # Update task fields
    updated_fields = []

    new_title = parameters.get("new_title")
    if new_title:
        task.title = new_title
        updated_fields.append("title")

    new_description = parameters.get("description")
    if new_description:
        task.description = new_description
        updated_fields.append("description")

    new_due_date = parameters.get("due_date")
    if new_due_date:
        task.due_date = new_due_date
        updated_fields.append("due date")

    new_priority = parameters.get("priority")
    if new_priority:
        task.priority = new_priority
        updated_fields.append("priority")

    new_status = parameters.get("status")
    if new_status:
        task.status = new_status
        updated_fields.append("status")

    db.commit()

    if not updated_fields:
        return "I didn't see any changes to make to the task. What would you like to update?", []

    return f"I've updated the {', '.join(updated_fields)} of task '{task.title}'.", [{"type": "task_updated", "task_id": task.id}]

def handle_delete_task(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle deleting a task."""
    task_id = parameters.get("task_id")
    title = parameters.get("title")

    if not task_id and not title:
        return "Which task would you like to delete?", []

    # Find the task
    query = db.query(Task).filter(Task.user_id == user.id)
    if task_id:
        task = query.filter(Task.id == task_id).first()
    else:
        # Try to find by title (partial match)
        task = query.filter(Task.title.ilike(f"%{title}%")).first()

    if not task:
        return "I couldn't find that task. Could you try again with a different task?", []

    task_title = task.title

    # Delete the task
    db.delete(task)
    db.commit()

    return f"I've deleted the task '{task_title}'.", [{"type": "task_deleted", "task_id": task_id}]

def handle_get_task_details(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle getting details about a task."""
    task_id = parameters.get("task_id")
    title = parameters.get("title")

    if not task_id and not title:
        return "Which task would you like to get details for?", []

    # Find the task
    query = db.query(Task).filter(Task.user_id == user.id)
    if task_id:
        task = query.filter(Task.id == task_id).first()
    else:
        # Try to find by title (partial match)
        task = query.filter(Task.title.ilike(f"%{title}%")).first()

    if not task:
        return "I couldn't find that task. Could you try again with a different task?", []

    # Format response
    response = f"Here are the details for task '{task.title}':\n\n"
    response += f"- Status: {task.status}\n"
    response += f"- Priority: {task.priority}\n"

    if task.description:
        response += f"- Description: {task.description}\n"

    if task.due_date:
        response += f"- Due date: {task.due_date.strftime('%Y-%m-%d')}\n"

    response += f"- Created: {task.created_at.strftime('%Y-%m-%d')}\n"

    return response, [{"type": "task_details", "task_id": task.id}]

def handle_change_priority(parameters: Dict[str, Any], user: User, db: Session) -> Tuple[str, List[Dict[str, Any]]]:
    """Handle changing the priority of a task."""
    task_id = parameters.get("task_id")
    title = parameters.get("title")
    priority = parameters.get("priority")

    if not priority:
        return "What priority would you like to set? (low, medium, high, or urgent)", []

    if not task_id and not title:
        return "Which task would you like to change the priority for?", []

    # Find the task
    query = db.query(Task).filter(Task.user_id == user.id)
    if task_id:
        task = query.filter(Task.id == task_id).first()
    else:
        # Try to find by title (partial match)
        task = query.filter(Task.title.ilike(f"%{title}%")).first()

    if not task:
        return "I couldn't find that task. Could you try again with a different task?", []

    # Update priority
    task.priority = priority
    db.commit()

    return f"I've changed the priority of '{task.title}' to {priority}.", [{"type": "task_updated", "task_id": task.id}]

def handle_help() -> Tuple[str, List[Dict[str, Any]]]:
    """Handle help request."""
    response = """I can help you manage your tasks. Here are some things you can ask me to do:

1. Add a task: "Add a task to call John tomorrow"
2. List tasks: "Show me my tasks" or "Show my high priority tasks"
3. Mark a task as complete: "Mark the call John task as done"
4. Update a task: "Change the due date of the meeting task to Friday"
5. Delete a task: "Delete the shopping task"
6. Get task details: "Tell me about the project presentation task"
7. Change priority: "Set the meeting task to high priority"

How can I help you today?"""

    return response, []
