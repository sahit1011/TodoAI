"""
Action Agent for Todo AI

This agent is responsible for:
1. Executing database operations based on user intent
2. Performing CRUD operations on tasks
3. Returning results and confirmation messages
4. Generating action events for frontend updates
"""

import json
import logging
import requests
import os
import re
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

# Import configuration
from backend.config import ASSISTANT_MODES

# Import SQLAlchemy
try:
    from sqlalchemy import or_
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    # Define fallback classes if SQLAlchemy is not available
    class SQLAlchemyError(Exception):
        pass
    def or_(*args):
        return args
from backend.models.task import Task

# Import UI action generator
from backend.agent.ui_action_generator import UIActionGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API endpoint and key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDTRUomc-KVV_Ib2oaKHcxnMQGXKPRFLxE")

class ActionAgent:
    def __init__(self, model_name=None):
        """Initialize the action agent with the Gemini API and UI action generator."""
        try:
            self.api_url = GEMINI_API_URL
            self.api_key = GEMINI_API_KEY
            # Initialize the UI action generator
            self.ui_action_generator = UIActionGenerator()
            logger.info("Action agent initialized with Gemini API and UI action generator")
        except Exception as e:
            logger.error(f"Error initializing action agent: {str(e)}")
            raise

    def _parse_due_date(self, due_date_str):
        """Parse natural language due date into a date object.

        Args:
            due_date_str (str): Natural language date string

        Returns:
            tuple: (date object or None, str or None, bool)
                - date object if successfully parsed, None otherwise
                - feedback message if date couldn't be parsed
                - boolean indicating if the date is valid
        """
        if not due_date_str:
            return None, None, True

        # Check if it's already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', due_date_str):
            try:
                return datetime.strptime(due_date_str, "%Y-%m-%d").date(), None, True
            except ValueError:
                return None, f"'{due_date_str}' is not a valid date format. Please use YYYY-MM-DD format.", False

        # Handle common natural language date expressions
        today = date.today()

        # Convert to lowercase for easier matching
        due_date_lower = due_date_str.lower()

        if due_date_lower in ['today', 'now']:
            return today, None, True

        elif due_date_lower in ['tomorrow', 'tmr', 'tmrw']:
            return today + timedelta(days=1), None, True

        elif due_date_lower in ['day after tomorrow', 'day after tmr']:
            return today + timedelta(days=2), None, True

        elif due_date_lower in ['next week', 'in a week']:
            return today + timedelta(days=7), None, True

        elif due_date_lower in ['next month', 'in a month']:
            # Approximate a month as 30 days
            return today + timedelta(days=30), None, True

        elif 'days' in due_date_lower or 'day' in due_date_lower:
            # Try to extract number of days
            match = re.search(r'(\d+)\s*days?', due_date_lower)
            if match:
                days = int(match.group(1))
                return today + timedelta(days=days), None, True

        # For other expressions like "tonight", "this evening", etc.
        # We can't parse these accurately without more context
        ambiguous_terms = ['tonight', 'this evening', 'this afternoon', 'this morning',
                          'soon', 'later', 'next', 'weekend', 'evening', 'afternoon',
                          'morning', 'night']

        if any(term in due_date_lower for term in ambiguous_terms):
            feedback = f"I couldn't convert '{due_date_str}' to a specific date. "
            feedback += "Please provide a date in YYYY-MM-DD format, or use terms like 'today', 'tomorrow', or 'next week'."
            return None, feedback, False

        # If we can't parse it, return None with feedback
        feedback = f"I couldn't understand the date '{due_date_str}'. "
        feedback += "Please provide a date in YYYY-MM-DD format, or use terms like 'today', 'tomorrow', or 'next week'."
        return None, feedback, False

    def _find_task_by_fuzzy_title(self, task_title, user, db):
        """Find a task by title with fuzzy matching."""
        # First try exact match
        exact_matches = db.query(Task).filter(Task.title == task_title, Task.user_id == user.id).all()
        if len(exact_matches) == 1:
            return exact_matches[0]
        elif len(exact_matches) > 1:
            # Multiple exact matches found - this is ambiguous
            # Return a special value to indicate ambiguity
            return {'ambiguous': True, 'matches': exact_matches}

        # If no exact match, try case-insensitive match
        tasks = db.query(Task).filter(Task.user_id == user.id).all()
        case_insensitive_matches = []

        # Try case-insensitive match
        for t in tasks:
            if t.title.lower() == task_title.lower():
                case_insensitive_matches.append(t)

        if len(case_insensitive_matches) == 1:
            return case_insensitive_matches[0]
        elif len(case_insensitive_matches) > 1:
            # Multiple case-insensitive matches found - this is ambiguous
            return {'ambiguous': True, 'matches': case_insensitive_matches}

        # If still no match, try partial match
        partial_matches = []
        for t in tasks:
            # Convert both to lowercase for comparison
            query = task_title.lower()
            title = t.title.lower()

            # Calculate different matching scores

            # 1. Word overlap score
            query_words = query.split()
            title_words = title.split()

            # Count exact word matches
            exact_word_matches = sum(1 for word in query_words if word in title_words)
            word_score = exact_word_matches / max(len(query_words), 1)  # Normalize by query length

            # 2. Substring score - check if query is a substring of title or vice versa
            substring_score = 0
            if query in title:
                substring_score = len(query) / len(title)  # Longer matches get higher scores
            elif title in query:
                substring_score = len(title) / len(query)

            # 3. Character overlap score
            char_overlap = sum(1 for c in query if c in title) / max(len(query), 1)

            # 4. Check for acronym match (e.g., "test multi agent" matching "TMA")
            acronym_score = 0
            if len(query) <= 5:  # Only check short queries that might be acronyms
                # Create acronym from title (first letter of each word)
                acronym = ''.join(word[0] for word in title_words if word)
                if query == acronym.lower():
                    acronym_score = 1.0

            # Combine scores with different weights
            score = (word_score * 0.5) + (substring_score * 0.3) + (char_overlap * 0.1) + (acronym_score * 0.1)

            # Add to matches if score is high enough
            if score > 0.3:  # Lower threshold to catch more potential matches
                partial_matches.append((t, score))

        # Sort by score in descending order
        partial_matches.sort(key=lambda x: x[1], reverse=True)

        if len(partial_matches) == 1:
            return partial_matches[0][0]
        elif len(partial_matches) > 1:
            # If the top match has a significantly higher score, return it
            if len(partial_matches) >= 2 and partial_matches[0][1] > partial_matches[1][1] + 0.3:
                return partial_matches[0][0]
            else:
                # Multiple partial matches with similar scores - this is ambiguous
                return {'ambiguous': True, 'matches': [match[0] for match in partial_matches]}

        # No matches found
        return None

    def execute_action(self, intent, parameters, user, db, assistant_mode=None):
        """
        Execute the requested action based on intent and parameters.

        Args:
            intent (str): The action intent (task_create, task_update, etc.)
            parameters (dict): Parameters for the action
            user (User): The current user object
            db (Session): Database session
            assistant_mode (str, optional): The assistant mode to use. If None, uses the user's preferred mode.

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Determine the assistant mode to use
            if assistant_mode is None:
                # Use the user's preferred mode
                assistant_mode = user.preferred_assistant_mode
                logger.info(f"Using user's preferred assistant mode: {assistant_mode}")
            else:
                logger.info(f"Using specified assistant mode: {assistant_mode}")

            # Log the action request
            logger.info(f"Executing action: {intent} with parameters: {parameters} in {assistant_mode} mode")

            # Execute the appropriate action based on intent and mode
            if assistant_mode == ASSISTANT_MODES["PLAN"]:
                # In PLAN mode, execute direct API actions without UI actions
                logger.info(f"Executing in PLAN mode: direct API actions")

                # Execute the appropriate action based on intent
                if intent == "task_create":
                    result = self._create_task(parameters, user, db, include_ui_actions=False)
                elif intent == "task_update":
                    result = self._update_task(parameters, user, db, include_ui_actions=False)
                elif intent == "task_delete":
                    result = self._delete_task(parameters, user, db, include_ui_actions=False)
                elif intent == "task_list":
                    result = self._list_tasks(parameters, user, db, include_ui_actions=False)
                elif intent == "task_complete":
                    result = self._complete_task(parameters, user, db, include_ui_actions=False)
                elif intent == "task_reopen":
                    result = self._reopen_task(parameters, user, db, include_ui_actions=False)
                else:
                    # For conversation intent, no action needed
                    result = {
                        "confirmation": "",
                        "actions": []
                    }

                return result

            else:  # ACT mode
                # In ACT mode, include UI actions
                logger.info(f"Executing in ACT mode: UI actions")

                # Execute the appropriate action based on intent
                if intent == "task_create":
                    return self._create_task(parameters, user, db, include_ui_actions=True)
                elif intent == "task_update":
                    return self._update_task(parameters, user, db, include_ui_actions=True)
                elif intent == "task_delete":
                    return self._delete_task(parameters, user, db, include_ui_actions=True)
                elif intent == "task_list":
                    return self._list_tasks(parameters, user, db, include_ui_actions=True)
                elif intent == "task_complete":
                    return self._complete_task(parameters, user, db, include_ui_actions=True)
                elif intent == "task_reopen":
                    return self._reopen_task(parameters, user, db, include_ui_actions=True)
                else:
                    # For conversation intent, no action needed
                    return {
                        "confirmation": "",
                        "actions": []
                    }
        except Exception as e:
            logger.error(f"Error in action agent: {str(e)}")
            error_message = str(e)

            # Create a user-friendly error message
            if "not found" in error_message.lower() and "Task with title similar to" in error_message:
                task_title = error_message.split("Task with title similar to")[1].split("not found")[0].strip().replace("'", "")
                if intent == "task_complete":
                    friendly_message = f"I couldn't mark that task as complete because I couldn't find any task matching '{task_title}'. Please check the task name or view your tasks to see what's available."
                elif intent == "task_update":
                    friendly_message = f"I couldn't update that task because I couldn't find any task matching '{task_title}'. Please check the task name or view your tasks to see what's available."
                elif intent == "task_delete":
                    friendly_message = f"I couldn't delete that task because I couldn't find any task matching '{task_title}'. Please check the task name or view your tasks to see what's available."
                elif intent == "task_reopen":
                    friendly_message = f"I couldn't reopen that task because I couldn't find any task matching '{task_title}'. Please check the task name or view your tasks to see what's available."
                else:
                    friendly_message = f"I couldn't find a task matching '{task_title}'. Please check the task name or create this task first."
            elif "not found" in error_message.lower() and "Task with ID" in error_message:
                task_id = error_message.split("Task with ID")[1].split("not found")[0].strip()
                friendly_message = f"I couldn't find a task with ID {task_id}. Please check the ID and try again."
            elif "ambiguous" in error_message.lower() or "multiple matching tasks" in error_message.lower():
                friendly_message = f"I found multiple tasks that match your request. Could you please be more specific or use the task ID?"
            else:
                # For other errors, don't expose the technical details
                friendly_message = f"I'm sorry, I couldn't complete that action. There was an issue with your request."
                logger.error(f"Technical error details (hidden from user): {error_message}")

            return {
                "confirmation": friendly_message,
                "actions": []
            }

    def _create_task(self, parameters, user, db, include_ui_actions=True):
        """Create a new task in the database.

        Args:
            parameters (dict): Parameters for creating the task
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Extract parameters
            title = parameters.get("title", "New Task")
            priority = parameters.get("priority", "medium").lower()
            due_date_str = parameters.get("due_date")

            # Validate priority
            if priority not in ["high", "medium", "low"]:
                priority = "medium"

            # Parse due date if provided
            due_date = None
            date_feedback = None
            if due_date_str:
                due_date, feedback, is_valid = self._parse_due_date(due_date_str)
                if not is_valid:
                    date_feedback = feedback
                    logger.warning(f"Invalid due date: {due_date_str}. {feedback}")

            # Import UI_FIRST_MODE from config
            from backend.config import UI_FIRST_MODE

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_create", parameters)
                logger.info(f"Generated UI actions for task_create: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Always create the task in the database, regardless of mode
            # We still return UI actions in Act mode for visual feedback
            logger.info("Creating task in database regardless of mode")

            # Create the task
            new_task = Task(
                title=title,
                priority=priority,
                status="todo",
                user_id=user.id,
                due_date=due_date
            )

            db.add(new_task)
            db.commit()
            db.refresh(new_task)

            # Generate confirmation using LLM
            confirmation_details = {
                "task_id": new_task.id,
                "title": title,
                "priority": priority
            }

            # Add due date information if available
            if due_date:
                confirmation_details["due_date"] = due_date.strftime("%Y-%m-%d")

            # Add date feedback if there was an issue
            if date_feedback:
                confirmation_details["date_feedback"] = date_feedback

            confirmation = self._generate_confirmation(
                "task_create",
                confirmation_details
            )

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_added", "task_id": new_task.id}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_added", "task_id": new_task.id}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating task: {str(e)}")
            raise

    def _update_task(self, parameters, user, db, include_ui_actions=True):
        """Update an existing task in the database.

        Args:
            parameters (dict): Parameters for updating the task
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Extract task ID or title
            task_id = parameters.get("task_id")
            task_title = parameters.get("task_title")

            # Find the task
            if task_id:
                # Find by ID
                task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
                if not task:
                    raise ValueError(f"Task with ID {task_id} not found")
            elif task_title:
                # Find by title with fuzzy matching
                result = self._find_task_by_fuzzy_title(task_title, user, db)

                if not result:
                    raise ValueError(f"Task with title similar to '{task_title}' not found")

                # Check if we have ambiguous matches
                if isinstance(result, dict) and result.get('ambiguous'):
                    matches = result.get('matches', [])
                    if not matches:
                        raise ValueError(f"Task with title similar to '{task_title}' not found")

                    # Format the ambiguous matches for the error message
                    match_details = [f"Task {t.id} (Title: '{t.title}', Priority: {t.priority})" for t in matches]
                    match_list = "\n- ".join(match_details)

                    raise ValueError(f"Found multiple matching tasks for '{task_title}'. Please specify which one by ID:\n- {match_list}")

                # We have a single match
                task = result
                task_id = task.id
            else:
                raise ValueError("Task ID or title is required for updates")

            # Track what was updated
            updates = {}

            # Update fields if provided
            if "title" in parameters:
                task.title = parameters["title"]
                updates["title"] = parameters["title"]

            if "priority" in parameters:
                priority = parameters["priority"].lower()
                if priority in ["high", "medium", "low"]:
                    task.priority = priority
                    updates["priority"] = priority

            if "status" in parameters:
                status = parameters["status"].lower()
                if status in ["todo", "in_progress", "done"]:
                    task.status = status
                    updates["status"] = status

            if "due_date" in parameters:
                due_date_str = parameters["due_date"]
                date_feedback = None

                if due_date_str:
                    due_date, feedback, is_valid = self._parse_due_date(due_date_str)
                    if is_valid:
                        task.due_date = due_date
                        updates["due_date"] = due_date.strftime("%Y-%m-%d") if due_date else None
                    else:
                        date_feedback = feedback
                        updates["date_feedback"] = feedback
                        logger.warning(f"Invalid due date: {due_date_str}. {feedback}")
                else:
                    task.due_date = None
                    updates["due_date"] = None

            # Save changes
            db.commit()

            # Generate confirmation using LLM
            confirmation = self._generate_confirmation(
                "task_update",
                {"task_id": task_id, "title": task.title, "updates": updates}
            )

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_update", {
                    "task_id": task_id,
                    "task_title": task.title,
                    "new_title": parameters.get("title", ""),
                    "priority": parameters.get("priority", ""),
                    "description": parameters.get("description", "")
                })
                logger.info(f"Generated UI actions for task_update: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task_id}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task_id}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating task: {str(e)}")
            raise

    def _delete_task(self, parameters, user, db, include_ui_actions=True):
        """Delete a task from the database.

        Args:
            parameters (dict): Parameters for deleting the task
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Check if we have task_id or task_title
            task_id = parameters.get("task_id")
            task_title = parameters.get("task_title")

            # Find the task
            if task_id:
                # Find by ID
                task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
                if not task:
                    raise ValueError(f"Task with ID {task_id} not found")
            elif task_title:
                # Find by title with fuzzy matching
                result = self._find_task_by_fuzzy_title(task_title, user, db)

                if not result:
                    raise ValueError(f"Task with title similar to '{task_title}' not found")

                # Check if we have ambiguous matches
                if isinstance(result, dict) and result.get('ambiguous'):
                    matches = result.get('matches', [])
                    if not matches:
                        raise ValueError(f"Task with title similar to '{task_title}' not found")

                    # Format the ambiguous matches for the error message
                    match_details = [f"Task {t.id} (Title: '{t.title}', Priority: {t.priority})" for t in matches]
                    match_list = "\n- ".join(match_details)

                    raise ValueError(f"Found multiple matching tasks for '{task_title}'. Please specify which one by ID:\n- {match_list}")

                # We have a single match
                task = result
            else:
                raise ValueError("Task ID or title is required for deletion")

            # Store task info for confirmation message
            task_id = task.id
            task_title = task.title

            # Delete the task
            db.delete(task)
            db.commit()

            # Generate confirmation using LLM
            confirmation = self._generate_confirmation(
                "task_delete",
                {"task_id": task_id, "title": task_title}
            )

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_delete", {
                    "task_id": task_id,
                    "task_title": task_title
                })
                logger.info(f"Generated UI actions for task_delete: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_deleted", "task_id": task_id}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_deleted", "task_id": task_id}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting task: {str(e)}")
            raise

    def _list_tasks(self, parameters, user, db, include_ui_actions=True):
        """List tasks based on filters.

        Args:
            parameters (dict): Parameters for filtering tasks
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Start with base query for user's tasks
            query = db.query(Task).filter(Task.user_id == user.id)

            # Apply filters if provided
            if "status" in parameters:
                status = parameters["status"].lower()
                # Map common status terms to database values
                if status in ["todo", "active", "pending"]:
                    query = query.filter(Task.status == "todo")
                elif status in ["done", "complete", "completed", "finished"]:
                    query = query.filter(Task.status == "done")
                elif status in ["in_progress", "ongoing"]:
                    query = query.filter(Task.status == "in_progress")

            if "priority" in parameters:
                priority = parameters["priority"].lower()
                if priority in ["high", "medium", "low"]:
                    query = query.filter(Task.priority == priority)

            # Handle search query if provided
            if "query" in parameters:
                search_query = parameters["query"].lower()
                if search_query:
                    # Split the search query into individual words
                    search_words = search_query.split()

                    # Remove common words that might interfere with search
                    common_words = ['a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'with', 'about', 'for', 'to', 'in', 'on', 'by', 'my']
                    search_words = [word for word in search_words if word.lower() not in common_words]

                    # If no meaningful search words remain, use the original query
                    if not search_words:
                        query = query.filter(Task.title.ilike(f'%{search_query}%'))
                    else:
                        # Create conditions for each word
                        conditions = []

                        # Add conditions for each word
                        for word in search_words:
                            conditions.append(Task.title.ilike(f'%{word}%'))

                        # Apply the OR conditions
                        if conditions:
                            query = query.filter(or_(*conditions))

            # Execute query
            tasks = query.all()

            # Format tasks for response
            task_list = []
            for task in tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                })

            # Format tasks for a more detailed confirmation in a user-friendly way
            active_tasks = [task for task in task_list if task['status'] == 'todo']
            completed_tasks = [task for task in task_list if task['status'] == 'done']

            # Check if we're filtering by status
            status_filter = parameters.get('status', '').lower()

            # Create a formatted string for active tasks with better formatting
            active_tasks_details = ""
            if active_tasks:
                active_tasks_details = "\n\n".join([f"• **Task {task['id']}:** {task['title']}\n  **Priority:** {task['priority'].capitalize()}" for task in active_tasks])

            # Create a formatted string for completed tasks with better formatting
            completed_tasks_details = ""
            if completed_tasks:
                completed_tasks_details = "\n\n".join([f"• **Task {task['id']}:** {task['title']}\n  **Priority:** {task['priority'].capitalize()}" for task in completed_tasks])

            # Check if this is a search query
            search_query = parameters.get('query', '')

            # Combine the details based on filter
            if search_query:
                # This is a search query, create a special header
                if tasks:
                    # Create a combined list of all matching tasks
                    search_results = []
                    for task in tasks:
                        # Access task attributes using dot notation
                        due_date_str = f", due {task.due_date.isoformat()}" if task.due_date else ""
                        status_str = "(Completed)" if task.status == 'done' else ""
                        search_results.append(f"• **Task {task.id}:** {task.title} {status_str}\n  **Priority:** {task.priority.capitalize()}{due_date_str}")

                    search_results_str = "\n\n".join(search_results)
                    task_details = f"### 🔍 Search Results for '{search_query}':\n\n{search_results_str}\n\n"
                else:
                    task_details = f"### 🔍 Search Results for '{search_query}':\n\nNo tasks found matching '{search_query}'.\n\n"
            elif status_filter == 'todo' or status_filter == 'active':
                # Only show active tasks
                task_details = f"### 📋 Your Active Tasks:\n\n{active_tasks_details if active_tasks else 'No active tasks at the moment.'}\n\n"
            elif status_filter == 'done' or status_filter == 'completed':
                # Only show completed tasks
                task_details = f"### ✅ Your Completed Tasks:\n\n{completed_tasks_details if completed_tasks else 'No completed tasks yet.'}\n\n"
            else:
                # Show both active and completed tasks
                task_details = f"### 📋 Your Active Tasks:\n\n{active_tasks_details if active_tasks else 'No active tasks at the moment.'}\n\n\n### ✅ Your Completed Tasks:\n\n{completed_tasks_details if completed_tasks else 'No completed tasks yet.'}\n\n"

            # Generate confirmation using LLM
            confirmation = self._generate_confirmation(
                "task_list",
                {"count": len(tasks), "filters": parameters, "task_details": task_details, "tasks": task_list}
            )

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_list", parameters)
                logger.info(f"Generated UI actions for task_list: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "tasks_listed", "tasks": task_list}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "tasks_listed", "tasks": task_list}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            logger.error(f"Database error listing tasks: {str(e)}")
            raise

    def _complete_task(self, parameters, user, db, include_ui_actions=True):
        """Mark a task as complete.

        Args:
            parameters (dict): Parameters for completing the task
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Check if we have task_id or task_title
            task_id = parameters.get("task_id")
            task_title = parameters.get("task_title")

            # Find the task
            if task_id:
                # Find by ID
                task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
                if not task:
                    raise ValueError(f"Task with ID {task_id} not found")
            elif task_title:
                # Find by title with fuzzy matching
                result = self._find_task_by_fuzzy_title(task_title, user, db)

                if not result:
                    raise ValueError(f"Task with title similar to '{task_title}' not found")

                # Check if we have ambiguous matches
                if isinstance(result, dict) and result.get('ambiguous'):
                    matches = result.get('matches', [])
                    if not matches:
                        raise ValueError(f"Task with title similar to '{task_title}' not found")

                    # Format the ambiguous matches for the error message
                    match_details = [f"Task {t.id} (Title: '{t.title}', Priority: {t.priority})" for t in matches]
                    match_list = "\n- ".join(match_details)

                    raise ValueError(f"Found multiple matching tasks for '{task_title}'. Please specify which one by ID:\n- {match_list}")

                # We have a single match
                task = result
            else:
                raise ValueError("Task ID or title is required")

            # Update status
            task.status = "done"
            db.commit()

            # Generate confirmation using LLM
            confirmation = self._generate_confirmation(
                "task_complete",
                {"task_id": task.id, "title": task.title}
            )

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_complete", {
                    "task_id": task.id,
                    "task_title": task.title
                })
                logger.info(f"Generated UI actions for task_complete: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task.id}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task.id}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error completing task: {str(e)}")
            raise

    def _reopen_task(self, parameters, user, db, include_ui_actions=True):
        """Reopen a completed task.

        Args:
            parameters (dict): Parameters for reopening the task
            user (User): The current user
            db (Session): Database session
            include_ui_actions (bool): Whether to include UI actions in the response

        Returns:
            dict: Contains confirmation message and actions for frontend
        """
        try:
            # Check if we have task_id or task_title
            task_id = parameters.get("task_id")
            task_title = parameters.get("task_title")

            # Find the task
            if task_id:
                # Find by ID
                task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
                if not task:
                    raise ValueError(f"Task with ID {task_id} not found")
            elif task_title:
                # Find by title with fuzzy matching
                result = self._find_task_by_fuzzy_title(task_title, user, db)

                if not result:
                    raise ValueError(f"Task with title similar to '{task_title}' not found")

                # Check if we have ambiguous matches
                if isinstance(result, dict) and result.get('ambiguous'):
                    matches = result.get('matches', [])
                    if not matches:
                        raise ValueError(f"Task with title similar to '{task_title}' not found")

                    # Format the ambiguous matches for the error message
                    match_details = [f"Task {t.id} (Title: '{t.title}', Priority: {t.priority})" for t in matches]
                    match_list = "\n- ".join(match_details)

                    raise ValueError(f"Found multiple matching tasks for '{task_title}'. Please specify which one by ID:\n- {match_list}")

                # We have a single match
                task = result
            else:
                raise ValueError("Task ID or title is required")

            # Update status
            task.status = "todo"
            db.commit()

            # Generate confirmation using LLM
            confirmation = self._generate_confirmation(
                "task_reopen",
                {"task_id": task.id, "title": task.title}
            )

            # Generate UI actions if needed
            ui_actions = []
            if include_ui_actions:
                ui_actions = self.ui_action_generator.generate_actions_for_intent("task_reopen", {
                    "task_id": task.id,
                    "task_title": task.title
                })
                logger.info(f"Generated UI actions for task_reopen: {ui_actions}")
            else:
                logger.info("Skipping UI action generation in PLAN mode")

            # Prepare the response based on whether UI actions are included
            if include_ui_actions:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task.id}, {"type": "ui_actions", "uiActions": ui_actions}],
                    "uiActions": ui_actions
                }
            else:
                return {
                    "confirmation": confirmation,
                    "actions": [{"type": "task_updated", "task_id": task.id}],
                    "uiActions": []
                }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error reopening task: {str(e)}")
            raise

    def _generate_confirmation(self, action_type, details):
        """Generate a natural language confirmation message using the LLM."""
        try:
            # Create prompt for confirmation generation
            if action_type == "task_list" and "task_details" in details:
                # Special handling for task lists to include the actual tasks
                status_filter = details.get('filters', {}).get('status', '')

                # Check if we're specifically looking for completed tasks
                if status_filter in ['done', 'completed']:
                    # Count how many completed tasks we have
                    completed_count = len([task for task in details.get('tasks', []) if task.get('status') == 'done'])

                    if completed_count == 0:
                        prompt = f"""
                        Generate a friendly response indicating that there are no completed tasks yet.
                        Keep it brief and encouraging.

                        Then include the exact task details as provided below (do not modify or reformat):
                        {details['task_details']}
                        """
                    else:
                        prompt = f"""
                        Generate a brief, friendly introduction for the completed task list, followed by the task details exactly as provided.

                        Your response should have this structure:
                        1. A brief, friendly greeting about completed tasks (1 sentence max)
                        2. The exact task details as provided below (do not modify or reformat):
                        {details['task_details']}

                        IMPORTANT INSTRUCTIONS:
                        - Keep your introduction very brief (1 sentence)
                        - DO NOT add any text between your introduction and the task details
                        - DO NOT modify the formatting of the task details in any way
                        - DO NOT repeat or summarize the tasks after showing them
                        - DO NOT add any additional task information beyond what is provided
                        - DO NOT create your own formatting for the tasks
                        """
                else:
                    # Check if this is a search query
                    filters = details.get('filters', {})
                    search_query = filters.get('query', '')

                    if search_query:
                        # For search queries
                        prompt = f"""
                        Generate a brief, friendly response for the search results, followed by the task details exactly as provided.

                        Search query: "{search_query}"
                        Number of results: {details.get('count', 0)}

                        Your response should have this structure:
                        1. A brief, friendly response about the search results (1 sentence max)
                        2. The exact task details as provided below (do not modify or reformat):
                        {details['task_details']}

                        IMPORTANT INSTRUCTIONS:
                        - Keep your introduction very brief (1 sentence)
                        - If no tasks were found, acknowledge this briefly
                        - DO NOT add any text between your introduction and the task details
                        - DO NOT modify the formatting of the task details in any way
                        - DO NOT repeat or summarize the tasks after showing them
                        - DO NOT add any additional task information beyond what is provided
                        - DO NOT create your own formatting for the tasks
                        """
                    else:
                        # For regular task lists
                        prompt = f"""
                        Generate a brief, friendly introduction for the task list, followed by the task details exactly as provided.

                        Number of tasks: {details.get('count', 0)}
                        Filters: {json.dumps(details.get('filters', {}))}

                        Your response should have this structure:
                        1. A brief, friendly greeting (1 sentence max)
                        2. The exact task details as provided below (do not modify or reformat):
                        {details['task_details']}

                        IMPORTANT INSTRUCTIONS:
                        - Keep your introduction very brief (1 sentence)
                        - DO NOT add any text between your introduction and the task details
                        - DO NOT modify the formatting of the task details in any way
                        - DO NOT repeat or summarize the tasks after showing them
                        - DO NOT add any additional task information beyond what is provided
                        - DO NOT create your own formatting for the tasks
                        - DO NOT use phrases like 'Here is' or 'Here are' in your introduction
                        """
            else:
                # Standard prompt for other actions
                if action_type == "task_create":
                    # Build the prompt with available details
                    task_details = f"""
                    Task ID: {details.get('task_id')}
                    Title: {details.get('title')}
                    Priority: {details.get('priority')}
                    """

                    # Add due date if available
                    if 'due_date' in details:
                        task_details += f"Due Date: {details.get('due_date')}\n"

                    # Add date feedback if there was an issue
                    date_feedback = ""
                    if 'date_feedback' in details:
                        date_feedback = f"\n\nNote about due date: {details.get('date_feedback')}\nPlease provide a date in YYYY-MM-DD format, or use terms like 'today', 'tomorrow', or 'next week'."

                    prompt = f"""
                    Generate a brief, friendly confirmation message for creating a new task.

                    {task_details}

                    Your response should be conversational and confirm the task was created successfully.
                    Don't include technical details like database IDs unless they're helpful to the user.{date_feedback}
                    """
                elif action_type == "task_update":
                    # Check if there's date feedback in the updates
                    updates = details.get('updates', {})
                    date_feedback = ""

                    if 'date_feedback' in updates:
                        date_feedback = f"\n\nNote about due date: {updates.get('date_feedback')}\nPlease provide a date in YYYY-MM-DD format, or use terms like 'today', 'tomorrow', or 'next week'."
                        # Remove the feedback from the updates to avoid showing it twice
                        updates_for_display = updates.copy()
                        updates_for_display.pop('date_feedback', None)
                    else:
                        updates_for_display = updates

                    prompt = f"""
                    Generate a brief, friendly confirmation message for updating a task.

                    Task ID: {details.get('task_id')}
                    Task Title: {details.get('title', 'Unknown')}
                    Updates: {json.dumps(updates_for_display)}

                    Your response should be conversational and confirm the task was updated successfully.
                    Focus on what was changed rather than technical details.
                    Include the task title in your response to confirm which task was updated.{date_feedback}
                    """
                elif action_type == "task_delete":
                    prompt = f"""
                    Generate a brief, friendly confirmation message for deleting a task.

                    Task ID: {details.get('task_id')}
                    Title: {details.get('title')}

                    Your response should be conversational and confirm the task was deleted successfully.
                    """
                elif action_type == "task_complete":
                    prompt = f"""
                    Generate a brief, friendly confirmation message for marking a task as complete.

                    Task ID: {details.get('task_id')}
                    Title: {details.get('title')}

                    Your response should be conversational, positive, and congratulatory for completing the task.
                    """
                elif action_type == "task_reopen":
                    prompt = f"""
                    Generate a brief, friendly confirmation message for reopening a completed task.

                    Task ID: {details.get('task_id')}
                    Title: {details.get('title')}

                    Your response should be conversational and confirm the task was reopened successfully.
                    """
                else:
                    # Generic prompt for other actions
                    prompt = f"""
                    Generate a brief, friendly confirmation message for the following action:

                    Action: {action_type}
                    Details: {json.dumps(details)}

                    The confirmation should be conversational and acknowledge what was done.
                    Avoid technical language and focus on what the user would want to know.
                    """

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
                    "maxOutputTokens": 256
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
                confirmation = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()

                # Clean up the response (remove quotes if present)
                if confirmation.startswith('"') and confirmation.endswith('"'):
                    confirmation = confirmation[1:-1]

                return confirmation
            else:
                # Handle API error
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                # Fall back to default confirmation
                return self._get_fallback_confirmation(action_type, details)
        except Exception as e:
            logger.error(f"Error generating confirmation: {str(e)}")
            return self._get_fallback_confirmation(action_type, details)

    def _get_fallback_confirmation(self, action_type, details):
        """Get a fallback confirmation message if the LLM fails."""
        if action_type == "task_create":
            title = details.get("title", "task")
            priority = details.get("priority", "")
            priority_text = f" with {priority} priority" if priority else ""
            return f"Great! I've created your task \"{title}\"{priority_text}."
        elif action_type == "task_update":
            updates = details.get("updates", {})
            update_text = ", ".join([f"{k}: {v}" for k, v in updates.items()])
            return f"I've updated your task with the new information{': ' + update_text if update_text else '.'}"
        elif action_type == "task_delete":
            title = details.get("title", "task")
            return f"I've deleted the task \"{title}\" as requested."
        elif action_type == "task_list":
            count = details.get("count", 0)
            task_details = details.get("task_details", "")
            if task_details:
                return f"Here are your {count} tasks:\n{task_details}"
            else:
                return f"I found {count} tasks for you."
        elif action_type == "task_complete":
            title = details.get("title", "task")
            return f"Great job! I've marked the task \"{title}\" as complete."
        elif action_type == "task_reopen":
            title = details.get("title", "task")
            return f"I've reopened the task \"{title}\" and moved it back to your active tasks."
        else:
            return "I've completed the requested action successfully."
