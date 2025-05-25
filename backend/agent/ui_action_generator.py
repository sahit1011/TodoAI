"""
UI Action Generator for Todo AI

This module generates UI action sequences that mimic how a user would interact with the UI
to perform various tasks. These actions are sent to the frontend to be executed by the
UIActionExecutor component.
"""

import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UIActionGenerator:
    """
    Generates UI action sequences for the frontend to execute.
    """

    def __init__(self):
        """Initialize the UI action generator."""
        logger.info("UI action generator initialized")

    def generate_actions_for_intent(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a sequence of UI actions based on the intent and parameters.

        Args:
            intent: The user's intent (task_create, task_list, etc.)
            parameters: Parameters for the action

        Returns:
            List of UI actions to execute
        """
        logger.info(f"Generating UI actions for intent: {intent}")

        if intent == "task_list":
            return self._generate_list_tasks_actions(parameters)
        elif intent == "task_create":
            return self._generate_create_task_actions(parameters)
        elif intent == "task_update":
            return self._generate_update_task_actions(parameters)
        elif intent == "task_complete":
            return self._generate_complete_task_actions(parameters)
        elif intent == "task_reopen":
            return self._generate_reopen_task_actions(parameters)
        elif intent == "task_delete":
            return self._generate_delete_task_actions(parameters)
        else:
            # For conversation or unknown intents, no UI actions
            return []

    def _generate_list_tasks_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for listing tasks."""
        actions = [
            {"type": "navigate", "target": "task_section"},
        ]

        # Determine which filter to apply
        filter_type = parameters.get("status", "active")
        logger.info(f"Generating UI actions for task list with filter_type: {filter_type}")

        if filter_type == "done" or filter_type == "completed" or filter_type == "complete":
            actions.append({"type": "click", "target": "completed_tasks_filter"})
            logger.info("Adding click action for completed_tasks_filter")
        elif filter_type == "todo" or filter_type == "active":
            actions.append({"type": "click", "target": "active_tasks_filter"})
            logger.info("Adding click action for active_tasks_filter")
        elif filter_type == "all":
            actions.append({"type": "click", "target": "all_tasks_filter"})
            logger.info("Adding click action for all_tasks_filter")

        logger.info(f"Generated UI actions for task list: {actions}")
        return actions

    def _generate_create_task_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for creating a task."""
        title = parameters.get("title", "New Task")
        priority = parameters.get("priority", "medium")
        description = parameters.get("description", "")

        actions = [
            {"type": "navigate", "target": "task_section"},
            {"type": "click", "target": "add_task_form"},
            {"type": "fill_form", "target": "add_task_form", "data": {
                "title": title,
                "priority": priority,
                "description": description
            }},
            {"type": "click", "target": "add_task_button"}
        ]

        return actions

    def _generate_update_task_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for updating a task."""
        task_id = parameters.get("task_id")
        task_title = parameters.get("task_title", "")

        actions = [
            {"type": "navigate", "target": "task_section"},
        ]

        # If we have a specific task ID, we can target it directly
        if task_id:
            actions.extend([
                {"type": "click", "target": f"edit_task_button_{task_id}"},
                {"type": "fill_form", "target": f"edit_task_form_{task_id}", "data": {
                    "title": parameters.get("new_title", ""),
                    "priority": parameters.get("priority", ""),
                    "description": parameters.get("description", "")
                }},
                {"type": "click", "target": f"save_task_button_{task_id}"}
            ])
        else:
            # Otherwise, we need to search for the task by title
            actions.append({"type": "search", "target": "task_search", "query": task_title})
            # Then click the first matching task's edit button
            actions.append({"type": "click", "target": "edit_first_matching_task"})
            # Fill the form
            actions.append({
                "type": "fill_form",
                "target": "edit_task_form",
                "data": {
                    "title": parameters.get("new_title", ""),
                    "priority": parameters.get("priority", ""),
                    "description": parameters.get("description", "")
                }
            })
            # Save the changes
            actions.append({"type": "click", "target": "save_task_button"})

        return actions

    def _generate_complete_task_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for completing a task."""
        task_id = parameters.get("task_id")
        task_title = parameters.get("task_title", "")

        actions = [
            {"type": "navigate", "target": "task_section"},
        ]

        # If we have a specific task ID, we can target it directly
        if task_id:
            actions.append({"type": "click", "target": f"complete_task_button_{task_id}"})
        else:
            # Otherwise, we need to search for the task by title
            actions.append({"type": "search", "target": "task_search", "query": task_title})
            # Then click the first matching task's complete button
            actions.append({"type": "click", "target": "complete_first_matching_task"})

        return actions

    def _generate_reopen_task_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for reopening a task."""
        task_id = parameters.get("task_id")
        task_title = parameters.get("task_title", "")

        actions = [
            {"type": "navigate", "target": "task_section"},
            {"type": "click", "target": "completed_tasks_filter"},
        ]

        # If we have a specific task ID, we can target it directly
        if task_id:
            actions.append({"type": "click", "target": f"reopen_task_button_{task_id}"})
        else:
            # Otherwise, we need to search for the task by title
            actions.append({"type": "search", "target": "task_search", "query": task_title})
            # Then click the first matching task's reopen button
            actions.append({"type": "click", "target": "reopen_first_matching_task"})

        return actions

    def _generate_delete_task_actions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI actions for deleting a task."""
        task_id = parameters.get("task_id")
        task_title = parameters.get("task_title", "")

        actions = [
            {"type": "navigate", "target": "task_section"},
        ]

        # If we have a specific task ID, we can target it directly
        if task_id:
            actions.append({"type": "click", "target": f"delete_task_button_{task_id}"})
            # Confirm deletion
            actions.append({"type": "click", "target": "confirm_delete_button"})
        else:
            # Otherwise, we need to search for the task by title
            actions.append({"type": "search", "target": "task_search", "query": task_title})
            # Then click the first matching task's delete button
            actions.append({"type": "click", "target": "delete_first_matching_task"})
            # Confirm deletion
            actions.append({"type": "click", "target": "confirm_delete_button"})

        return actions
