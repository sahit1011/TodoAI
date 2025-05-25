"""
Multi-Agent Coordinator for Todo AI

This module coordinates the interaction between the conversational agent and the action agent.
It manages the flow of information and ensures proper handling of user requests.
"""

import logging
from .conversational_agent import ConversationalAgent
from .action_agent import ActionAgent
from backend.config import ASSISTANT_MODES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiAgentCoordinator:
    def __init__(self, conversation_model=None, action_model=None):
        """Initialize the multi-agent system with the Gemini API."""
        try:
            self.conversational_agent = ConversationalAgent()
            self.action_agent = ActionAgent()
            logger.info("Multi-agent system initialized with Gemini API")
        except Exception as e:
            logger.error(f"Error initializing multi-agent system: {str(e)}")
            raise

    def process_message(self, message, conversation_history, user, db, assistant_mode=None):
        """
        Process a user message through the multi-agent system.

        Args:
            message (str): The user's message
            conversation_history (list): Previous conversation turns
            user (User): The current user object
            db (Session): Database session
            assistant_mode (str, optional): The assistant mode to use. If None, uses the user's preferred mode.

        Returns:
            tuple: (response_text, actions)
        """
        try:
            # Determine the assistant mode to use
            if assistant_mode is None:
                # Use the user's preferred mode
                assistant_mode = user.preferred_assistant_mode
                logger.info(f"Using user's preferred assistant mode: {assistant_mode}")
            else:
                logger.info(f"Using specified assistant mode: {assistant_mode}")

            # Step 1: Process the message with the conversational agent
            logger.info(f"Processing message with conversational agent: {message}")
            conversation_result = self.conversational_agent.process_message(
                message, conversation_history, user, db
            )

            # Extract intent, parameters, and response
            intent = conversation_result.get("intent", "conversation")
            parameters = conversation_result.get("parameters", {})
            response = conversation_result.get("response", "")

            logger.info(f"Conversational agent determined intent: {intent}")

            # Step 2: If it's a task-related intent, check if we need more information
            actions = []
            action_confirmation = ""

            # Check if the conversational agent is asking for more information
            is_asking_for_info = False

            # Patterns that indicate the agent is asking for more information
            asking_patterns = [
                # Direct questions about information
                "could you please provide", "i need more information", "can you clarify",
                "could you specify", "which one do you mean", "please provide more details",
                "i'm not sure which", "can you be more specific", "please clarify",
                # Questions about task details
                "what priority", "what due date", "when is it due", "which task",
                "what would you like", "what title", "what description",
                # General question patterns
                "could you tell me", "would you like", "do you want", "should i",
                "what would you", "which would you", "how would you", "when would you",
                # Question marks
                "?"
            ]

            # Check for question patterns
            for pattern in asking_patterns:
                if pattern.lower() in response.lower():
                    is_asking_for_info = True
                    logger.info(f"Conversational agent is asking for more information: {response}")
                    break

            # First check if it's a confirmation question, which should always be treated as not asking for info
            if "?" in response and any(phrase in response.lower() for phrase in ["anything else", "can i help", "would you like", "is there anything else"]):
                is_asking_for_info = False
                logger.info(f"Conversational agent is asking a confirmation question, not treating as information request: {response}")
            # Then check if it's asking for task-related information
            elif "?" in response and any(param in response.lower() for param in ["priority", "due date", "title", "description", "when", "what"]):
                is_asking_for_info = True
                logger.info(f"Conversational agent is asking a task-related question: {response}")

            # Check if the intent is task_update but priority or other key fields are missing
            if intent == "task_update" and parameters.get("priority") is None and "priority" in response.lower():
                is_asking_for_info = True
                logger.info(f"Conversational agent is asking about priority: {response}")

            # Check if the intent is task_create but title is missing
            if intent == "task_create" and not parameters.get("title"):
                is_asking_for_info = True
                logger.info(f"Conversational agent is asking about task title: {response}")

            # Only execute the action if we're not asking for more information
            if intent != "conversation" and not is_asking_for_info:
                logger.info(f"Executing action with action agent: {intent}")
                try:
                    # Pass the assistant mode to the action agent
                    action_result = self.action_agent.execute_action(
                        intent, parameters, user, db, assistant_mode
                    )

                    # Get the confirmation and actions
                    action_confirmation = action_result.get("confirmation", "")
                    actions = action_result.get("actions", [])

                    # Action was successful, we can use the conversational agent's response
                    # or the action agent's confirmation
                except Exception as e:
                    logger.error(f"Error in action agent: {str(e)}")
                    # If the action fails, we should NOT use the conversational agent's response
                    # as it might be incorrect (e.g., saying a task was completed when it wasn't)
                    error_message = str(e)

                    # Create a user-friendly error message based on the error type
                    if "not found" in error_message.lower():
                        if "Task with title" in error_message:
                            task_title = error_message.split("Task with title")[1].split("not found")[0].strip().replace("'", "")
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
                        elif "Task with ID" in error_message:
                            task_id = error_message.split("Task with ID")[1].split("not found")[0].strip()
                            friendly_message = f"I couldn't find a task with ID {task_id}. Please check the ID and try again."
                        else:
                            friendly_message = f"I couldn't find the task you're referring to. Please check the task name or ID."
                    elif "ambiguous" in error_message.lower() or "multiple matching tasks" in error_message.lower():
                        friendly_message = f"I found multiple tasks that match your request. Could you please be more specific or use the task ID?"
                    else:
                        # For other errors, create a user-friendly error message
                        friendly_message = f"I'm sorry, I couldn't complete that action. There was an issue with your request."
                        logger.error(f"Technical error details (hidden from user): {error_message}")

                    # Set action_confirmation to empty to indicate the action failed
                    action_confirmation = ""

                    # Raise a custom exception with the friendly message
                    # This will be caught by the outer try-except block
                    raise Exception(friendly_message)
            elif is_asking_for_info:
                # If we're asking for more information, don't execute the action
                logger.info("Skipping action execution because more information is needed")

            # Step 3: Combine the response and confirmation
            final_response = response

            # Only use action_confirmation if it exists (meaning the action was successful)
            if action_confirmation:
                # For task listing, use only the action agent's response
                if intent == "task_list":
                    final_response = action_confirmation
                else:
                    # Don't include the original response if it's just a simple acknowledgment
                    if response.startswith("OK.") or response.startswith("I'll") or response.startswith("I've"):
                        final_response = action_confirmation
                    else:
                        # If the response already contains the action confirmation, don't duplicate it
                        if action_confirmation in response:
                            final_response = response
                        else:
                            final_response = f"{response} {action_confirmation}"

            return final_response, actions
        except Exception as e:
            logger.error(f"Error in multi-agent coordinator: {str(e)}")
            error_message = str(e)

            # Create a user-friendly response based on the error type
            if "Found multiple matching tasks" in error_message:
                # This is an ambiguity error, extract the task details
                tasks_info = error_message.split("Please specify which one by ID:")[1].strip() if "Please specify which one by ID:" in error_message else ""
                return f"I found multiple tasks that match your request. Could you please specify which one you'd like to work with?{tasks_info}", []

            elif "not found" in error_message and ("Task with ID" in error_message or "Task with title" in error_message):
                # Task not found error
                if "Task with ID" in error_message:
                    task_id = error_message.split("Task with ID")[1].split("not found")[0].strip()
                    return f"I couldn't find a task with ID {task_id}. Please check the ID and try again.", []
                else:
                    task_title = error_message.split("Task with title")[1].split("not found")[0].strip().replace("'", "")
                    return f"I couldn't find a task with the title \"{task_title}\". Please check the title or create this task first.", []

            elif "Task ID or title is required" in error_message:
                # Missing task identifier
                return f"I need to know which task you're referring to. Please specify the task title or ID.", []

            elif "Invalid due date format" in error_message:
                # Invalid date format
                date_str = error_message.split("Invalid due date format:")[1].strip() if "Invalid due date format:" in error_message else "the date you provided"
                return f"I couldn't understand the date format '{date_str}'. Please use YYYY-MM-DD format (e.g., 2025-12-31).", []

            else:
                # Generic error - don't expose technical details to the user
                logger.error(f"Technical error (hidden from user): {error_message}")
                return "I'm sorry, I encountered an issue while processing your request. Could you please try again or rephrase your request?", []
