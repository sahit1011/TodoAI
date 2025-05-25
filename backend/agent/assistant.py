import os
import openai
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from dotenv import load_dotenv

from backend.models.user import User
from backend.models.task import Task, PriorityEnum, StatusEnum

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
from openai import ChatCompletion

# Define intents
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
    # Import the multi-agent process function
    from backend.agent.multi_agent_process import multi_agent_process

    # Use the multi-agent system to process the message
    return multi_agent_process(message, conversation_context, user, db)

def classify_intent(message: str, conversation_context: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
    """
    Classify the intent of a user message and extract parameters.

    Args:
        message: The user's message
        conversation_context: The conversation history

    Returns:
        Tuple of (intent, parameters)
    """
    # Prepare the prompt for OpenAI
    system_prompt = """
    You are an AI assistant for a todo list application. Your job is to:
    1. Identify the user's intent from their message
    2. Extract relevant parameters for that intent

    Respond with a JSON object containing:
    {
        "intent": "intent_name",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }

    Available intents:
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

    For dates, convert to ISO format (YYYY-MM-DD).
    For priorities, use: low, medium, high, urgent
    For status, use: todo, in_progress, done, archived
    """

    # Create messages for the API call
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add conversation context (limited to last few messages)
    context_to_include = conversation_context[-5:] if len(conversation_context) > 5 else conversation_context
    messages.extend(context_to_include)

    try:
        # Call OpenAI API with old version format
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use appropriate model
            messages=messages,
            temperature=0.1,  # Low temperature for more deterministic responses
            max_tokens=500
        )

        # Parse the response
        content = response.choices[0].message.content

        # Extract JSON from the response
        import json
        import re

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            intent = result.get("intent", "unknown")
            parameters = result.get("parameters", {})
        else:
            intent = "unknown"
            parameters = {}

        return intent, parameters

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
    actions = []

    try:
        if intent == "add_task":
            return handle_add_task(parameters, user, db, actions)

        elif intent == "list_tasks":
            return handle_list_tasks(parameters, user, db, actions)

        elif intent == "get_task_details":
            return handle_get_task_details(parameters, user, db, actions)

        elif intent == "update_task":
            return handle_update_task(parameters, user, db, actions)

        elif intent == "delete_task":
            return handle_delete_task(parameters, user, db, actions)

        elif intent == "mark_complete":
            return handle_mark_complete(parameters, user, db, actions)

        elif intent == "change_priority":
            return handle_change_priority(parameters, user, db, actions)

        elif intent == "help":
            return handle_help(actions)

        else:
            # Handle unknown intent
            return "I'm not sure what you want to do. Can you please be more specific?", actions

    except Exception as e:
        print(f"Error executing action: {e}")
        return f"Sorry, I encountered an error: {str(e)}", actions

def handle_add_task(parameters, user, db, actions):
    """Handle adding a new task"""
    title = parameters.get("title")
    if not title:
        return "What would you like to name this task?", actions

    description = parameters.get("description", "")

    # Handle due date
    due_date = None
    if "due_date" in parameters and parameters["due_date"]:
        try:
            due_date = datetime.fromisoformat(parameters["due_date"].replace("Z", "+00:00"))
        except ValueError:
            # If date parsing fails, leave as None
            pass

    # Handle priority
    priority = PriorityEnum.MEDIUM
    if "priority" in parameters:
        priority_str = parameters["priority"].lower()
        if priority_str in [p.value for p in PriorityEnum]:
            priority = PriorityEnum(priority_str)

    # Create the task
    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        status=StatusEnum.TODO,
        user_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Record the action
    actions.append({
        "action": "add_task",
        "task_id": str(new_task.id),
        "title": new_task.title
    })

    # Generate response
    response = f"I've added the task '{title}' to your list."
    if due_date:
        response += f" It's due on {due_date.strftime('%B %d, %Y')}."
    if priority != PriorityEnum.MEDIUM:
        response += f" I've set the priority to {priority.value}."

    return response, actions

def handle_list_tasks(parameters, user, db, actions):
    """Handle listing tasks"""
    # Get filter parameters
    status = parameters.get("status")
    priority = parameters.get("priority")

    # Build query
    query = db.query(Task).filter(Task.user_id == user.id)

    # Apply filters
    if status:
        if status in [s.value for s in StatusEnum]:
            query = query.filter(Task.status == StatusEnum(status))

    if priority:
        if priority in [p.value for p in PriorityEnum]:
            query = query.filter(Task.priority == PriorityEnum(priority))

    # Execute query
    tasks = query.all()

    # Record action
    actions.append({
        "action": "list_tasks",
        "count": len(tasks),
        "filters": {
            "status": status,
            "priority": priority
        }
    })

    # Generate response
    if not tasks:
        if status or priority:
            response = "I couldn't find any tasks matching those filters."
        else:
            response = "You don't have any tasks yet. Would you like to add one?"
    else:
        response = f"Here are your tasks ({len(tasks)}):\n\n"
        for i, task in enumerate(tasks, 1):
            due_str = f" (Due: {task.due_date.strftime('%b %d')})" if task.due_date else ""
            priority_str = f" [{task.priority.value}]" if task.priority != PriorityEnum.MEDIUM else ""
            response += f"{i}. {task.title}{priority_str}{due_str} - {task.status.value}\n"

    return response, actions

def handle_get_task_details(parameters, user, db, actions):
    """Handle getting details about a specific task"""
    # Get task identifier
    task_id = parameters.get("task_id")
    task_title = parameters.get("title")

    # Find the task
    task = None
    if task_id:
        try:
            task = db.query(Task).filter(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            ).first()
        except ValueError:
            # Invalid UUID format
            pass

    if not task and task_title:
        # Try to find by title (partial match)
        tasks = db.query(Task).filter(
            Task.title.ilike(f"%{task_title}%"),
            Task.user_id == user.id
        ).all()

        if len(tasks) == 1:
            task = tasks[0]
        elif len(tasks) > 1:
            # Multiple matches
            response = "I found multiple tasks with that title. Please be more specific:\n\n"
            for i, t in enumerate(tasks[:5], 1):
                response += f"{i}. {t.title}\n"
            if len(tasks) > 5:
                response += f"...and {len(tasks) - 5} more."
            return response, actions

    if not task:
        return "I couldn't find that task. Can you provide more details?", actions

    # Record action
    actions.append({
        "action": "get_task_details",
        "task_id": str(task.id)
    })

    # Generate response
    response = f"Here are the details for '{task.title}':\n\n"
    response += f"Status: {task.status.value}\n"
    response += f"Priority: {task.priority.value}\n"

    if task.due_date:
        response += f"Due date: {task.due_date.strftime('%B %d, %Y')}\n"

    if task.description:
        response += f"\nDescription: {task.description}\n"

    response += f"\nCreated: {task.created_at.strftime('%B %d, %Y')}"

    return response, actions

def handle_update_task(parameters, user, db, actions):
    """Handle updating a task"""
    # Get task identifier
    task_id = parameters.get("task_id")
    task_title = parameters.get("title")

    # Find the task
    task = None
    if task_id:
        try:
            task = db.query(Task).filter(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            ).first()
        except ValueError:
            # Invalid UUID format
            pass

    if not task and task_title:
        # Try to find by title (partial match)
        tasks = db.query(Task).filter(
            Task.title.ilike(f"%{task_title}%"),
            Task.user_id == user.id
        ).all()

        if len(tasks) == 1:
            task = tasks[0]
        elif len(tasks) > 1:
            # Multiple matches
            response = "I found multiple tasks with that title. Please be more specific:\n\n"
            for i, t in enumerate(tasks[:5], 1):
                response += f"{i}. {t.title}\n"
            if len(tasks) > 5:
                response += f"...and {len(tasks) - 5} more."
            return response, actions

    if not task:
        return "I couldn't find that task. Can you provide more details?", actions

    # Get update parameters
    updates = {}

    if "new_title" in parameters:
        updates["title"] = parameters["new_title"]

    if "description" in parameters:
        updates["description"] = parameters["description"]

    if "due_date" in parameters:
        try:
            updates["due_date"] = datetime.fromisoformat(parameters["due_date"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    if "priority" in parameters:
        priority_str = parameters["priority"].lower()
        if priority_str in [p.value for p in PriorityEnum]:
            updates["priority"] = PriorityEnum(priority_str)

    if "status" in parameters:
        status_str = parameters["status"].lower()
        if status_str in [s.value for s in StatusEnum]:
            updates["status"] = StatusEnum(status_str)

    # Apply updates
    for key, value in updates.items():
        setattr(task, key, value)

    db.commit()

    # Record action
    actions.append({
        "action": "update_task",
        "task_id": str(task.id),
        "updates": list(updates.keys())
    })

    # Generate response
    response = f"I've updated the task '{task.title}'."

    return response, actions

def handle_delete_task(parameters, user, db, actions):
    """Handle deleting a task"""
    # Get task identifier
    task_id = parameters.get("task_id")
    task_title = parameters.get("title")

    # Find the task
    task = None
    if task_id:
        try:
            task = db.query(Task).filter(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            ).first()
        except ValueError:
            # Invalid UUID format
            pass

    if not task and task_title:
        # Try to find by title (partial match)
        tasks = db.query(Task).filter(
            Task.title.ilike(f"%{task_title}%"),
            Task.user_id == user.id
        ).all()

        if len(tasks) == 1:
            task = tasks[0]
        elif len(tasks) > 1:
            # Multiple matches
            response = "I found multiple tasks with that title. Please be more specific:\n\n"
            for i, t in enumerate(tasks[:5], 1):
                response += f"{i}. {t.title}\n"
            if len(tasks) > 5:
                response += f"...and {len(tasks) - 5} more."
            return response, actions

    if not task:
        return "I couldn't find that task. Can you provide more details?", actions

    # Store task info before deletion
    task_title = task.title
    task_id = str(task.id)

    # Delete the task
    db.delete(task)
    db.commit()

    # Record action
    actions.append({
        "action": "delete_task",
        "task_id": task_id,
        "title": task_title
    })

    # Generate response
    response = f"I've deleted the task '{task_title}'."

    return response, actions

def handle_mark_complete(parameters, user, db, actions):
    """Handle marking a task as complete"""
    # Get task identifier
    task_id = parameters.get("task_id")
    task_title = parameters.get("title")

    # Find the task
    task = None
    if task_id:
        try:
            task = db.query(Task).filter(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            ).first()
        except ValueError:
            # Invalid UUID format
            pass

    if not task and task_title:
        # Try to find by title (partial match)
        tasks = db.query(Task).filter(
            Task.title.ilike(f"%{task_title}%"),
            Task.user_id == user.id
        ).all()

        if len(tasks) == 1:
            task = tasks[0]
        elif len(tasks) > 1:
            # Multiple matches
            response = "I found multiple tasks with that title. Please be more specific:\n\n"
            for i, t in enumerate(tasks[:5], 1):
                response += f"{i}. {t.title}\n"
            if len(tasks) > 5:
                response += f"...and {len(tasks) - 5} more."
            return response, actions

    if not task:
        return "I couldn't find that task. Can you provide more details?", actions

    # Update the task status
    task.status = StatusEnum.DONE
    db.commit()

    # Record action
    actions.append({
        "action": "mark_complete",
        "task_id": str(task.id),
        "title": task.title
    })

    # Generate response
    response = f"I've marked the task '{task.title}' as complete. Great job!"

    return response, actions

def handle_change_priority(parameters, user, db, actions):
    """Handle changing a task's priority"""
    # Get task identifier
    task_id = parameters.get("task_id")
    task_title = parameters.get("title")

    # Get priority
    priority_str = parameters.get("priority", "").lower()
    if not priority_str or priority_str not in [p.value for p in PriorityEnum]:
        return "What priority would you like to set? (low, medium, high, or urgent)", actions

    priority = PriorityEnum(priority_str)

    # Find the task
    task = None
    if task_id:
        try:
            task = db.query(Task).filter(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            ).first()
        except ValueError:
            # Invalid UUID format
            pass

    if not task and task_title:
        # Try to find by title (partial match)
        tasks = db.query(Task).filter(
            Task.title.ilike(f"%{task_title}%"),
            Task.user_id == user.id
        ).all()

        if len(tasks) == 1:
            task = tasks[0]
        elif len(tasks) > 1:
            # Multiple matches
            response = "I found multiple tasks with that title. Please be more specific:\n\n"
            for i, t in enumerate(tasks[:5], 1):
                response += f"{i}. {t.title}\n"
            if len(tasks) > 5:
                response += f"...and {len(tasks) - 5} more."
            return response, actions

    if not task:
        return "I couldn't find that task. Can you provide more details?", actions

    # Update the task priority
    task.priority = priority
    db.commit()

    # Record action
    actions.append({
        "action": "change_priority",
        "task_id": str(task.id),
        "priority": priority.value
    })

    # Generate response
    response = f"I've changed the priority of '{task.title}' to {priority.value}."

    return response, actions

def handle_help(actions):
    """Handle help request"""
    # Record action
    actions.append({
        "action": "help"
    })

    # Generate response
    response = """
    I'm your AI-powered todo list assistant. Here's what I can help you with:

    - **Adding tasks**: "Add a task to buy groceries tomorrow"
    - **Listing tasks**: "Show me all my tasks" or "What are my high priority tasks?"
    - **Task details**: "Tell me more about the grocery task"
    - **Updating tasks**: "Change the due date of my report task to Friday"
    - **Completing tasks**: "Mark the grocery task as done"
    - **Deleting tasks**: "Delete the meeting task"
    - **Changing priorities**: "Set the report task to high priority"

    You can talk to me naturally, and I'll do my best to understand what you need!
    """

    return response, actions
