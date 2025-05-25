"""
Documentation store for the Todo AI application.
This module contains documentation sections organized by topic for retrieval.
"""

class DocumentationStore:
    """
    A store for application documentation that can retrieve relevant sections
    based on user queries.
    """

    def __init__(self):
        # Initialize documentation sections
        self.documentation_sections = {
            "overview": """
                # Todo AI Application Overview

                Todo AI is a task management application that helps users organize and track their tasks.
                It features a natural language interface that allows users to create, view, update, and delete tasks
                using conversational language.
            """,

            "priority": """
                # Priority

                Priority indicates the importance or urgency of a task:
                - **High**: Critical tasks that should be completed as soon as possible
                - **Medium**: Important tasks but not urgent
                - **Low**: Tasks that can be completed when time permits

                You can change a task's priority by saying "Change the priority of [task name] to [high/medium/low]"
                or "Update [task name] to [high/medium/low] priority".
            """,

            "task_status": """
                # Task Status

                Status indicates the completion state of a task:
                - **Todo**: Tasks that are active and need to be completed
                - **Done**: Tasks that have been completed

                You can mark a task as complete by saying "Mark [task name] as complete"
                You can reopen a task by saying "Reopen [task name]"
            """,

            "creating_tasks": """
                # Creating Tasks

                Users can create new tasks by specifying a title and optionally a priority and due date.

                Examples:
                - "Create a task called 'Buy groceries' with high priority"
                - "Add a new task: 'Call mom' with medium priority due tomorrow"
                - "I need to submit my report by Friday"
            """,

            "viewing_tasks": """
                # Viewing Tasks

                Users can view their tasks with optional filters for status and priority.

                Examples:
                - "Show me all my tasks"
                - "Show my active tasks"
                - "List my high priority tasks"
                - "Show my completed tasks"

                Users can also search for specific tasks by keywords in the title:
                - "Find tasks about groceries"
                - "Search for tasks related to mom"
                - "Do I have any tasks about reports?"
                - "Show me tasks with meeting in the title"
            """,

            "updating_tasks": """
                # Updating Tasks

                Users can update task properties such as title, priority, and due date.

                Examples:
                - "Change the priority of 'Buy groceries' to medium"
                - "Update the due date of 'Call mom' to next Friday"
                - "Rename task 'Buy groceries' to 'Shop for groceries'"
            """,

            "completing_tasks": """
                # Completing Tasks

                Users can mark tasks as complete.

                Examples:
                - "Mark 'Buy groceries' as complete"
                - "Complete the task 'Call mom'"
                - "I finished the 'Submit report' task"
            """,

            "reopening_tasks": """
                # Reopening Tasks

                Users can reopen completed tasks.

                Examples:
                - "Reopen the 'Buy groceries' task"
                - "Mark 'Call mom' as not done"
                - "I need to redo the 'Submit report' task"
            """,

            "deleting_tasks": """
                # Deleting Tasks

                Users can delete tasks they no longer need.

                Examples:
                - "Delete the 'Buy groceries' task"
                - "Remove task 'Call mom'"
                - "Get rid of the 'Submit report' task"
            """,

            "due_dates": """
                # Due Dates

                Tasks can have optional due dates to indicate when they should be completed.

                You can set a due date when creating a task:
                - "Create a task called 'Submit report' due tomorrow"
                - "Add a task to call mom with due date next week"

                Or update an existing task's due date:
                - "Change the due date of 'Submit report' to next Monday"
                - "Update the deadline for my grocery shopping task to today"

                The app accepts the following date formats:
                - Specific dates in YYYY-MM-DD format (e.g., "2023-12-31")
                - Natural language terms like "today", "tomorrow", "next week", "next month"
                - Relative terms like "in 3 days", "in a week"

                For ambiguous terms like "tonight" or "this evening", the app will ask for clarification
                and request a more specific date format.
            """,

            "capabilities": """
                # App Capabilities

                The Todo AI app can:
                1. Create tasks with title, priority, and optional due date
                2. List tasks with filters (active, completed, priority)
                3. Update task details (title, priority, due date)
                4. Mark tasks as complete
                5. Reopen completed tasks
                6. Delete tasks

                All of these actions can be performed using natural language commands.
            """,

            "limitations": """
                # App Limitations

                The Todo AI app is specifically designed for task management and has several limitations on actions it can perform:

                1. It CANNOT send emails, messages, or communicate with external services
                2. It CANNOT make phone calls or contact people
                3. It CANNOT access the internet or search the web in real-time
                4. It CANNOT perform actions outside of task management
                5. It CANNOT access or modify files on your computer
                6. It CANNOT schedule meetings or manage your calendar

                The app is primarily designed for managing tasks within the application.
                When users ask for actions outside these boundaries, the assistant should
                politely explain that it cannot perform those actions and suggest using the
                app for its intended purpose of task management.

                However, the assistant CAN answer general knowledge questions using its built-in knowledge.
                For example, it can explain concepts, provide definitions, or share general information
                that doesn't require real-time web access. The assistant should be helpful and informative
                when responding to general questions, while still being clear about its limitations regarding
                actions it cannot perform.
            """
        }

        # Keywords that indicate which section might be relevant
        self.section_keywords = {
            "overview": ["what is", "about", "tell me about", "how does", "what does", "app do",
                        "purpose", "overview", "summary", "introduction"],
            "priority": ["priority", "important", "urgency", "high", "medium", "low", "importance"],
            "task_status": ["status", "complete", "done", "active", "todo", "finished", "incomplete",
                           "pending", "state", "completion"],
            "creating_tasks": ["create", "add", "new task", "make", "start"],
            "viewing_tasks": ["view", "show", "list", "see", "display", "find", "search", "look for", "locate", "query", "filter"],
            "updating_tasks": ["update", "change", "modify", "edit", "rename", "alter"],
            "completing_tasks": ["complete", "finish", "mark done", "mark as done", "mark complete",
                               "mark as complete", "completed", "done"],
            "reopening_tasks": ["reopen", "undo complete", "mark as todo", "mark as not done",
                              "unfinish", "uncomplete"],
            "deleting_tasks": ["delete", "remove", "get rid", "erase", "trash"],
            "due_dates": ["due date", "deadline", "when", "by when", "due", "schedule"],
            "capabilities": ["can do", "able to", "capabilities", "features", "functions",
                           "what can", "help with", "abilities", "what all", "perform"],
            "limitations": ["cannot", "can't", "unable to", "not able", "limitations", "limits",
                          "restricted", "doesn't work", "won't work", "impossible",
                          "email", "call", "text", "message", "send", "contact", "schedule",
                          "meeting", "calendar", "outside", "external", "internet", "web"]
        }

    def get_relevant_sections(self, message):
        """
        Determine which documentation sections are relevant to the message.

        Args:
            message (str): The user's message

        Returns:
            list: List of relevant section names
        """
        message = message.lower()
        relevant_sections = []

        # Check for out-of-scope action requests first
        out_of_scope_action_indicators = [
            "email", "send email", "send a message", "text", "sms", "call", "phone",
            "contact", "reach out", "communicate with", "tell", "inform", "notify",
            "schedule meeting", "book appointment", "calendar", "agenda",
            "download", "upload", "file", "document", "access", "external"
        ]

        # Check if this is a general knowledge question
        general_knowledge_indicators = [
            "what is", "how does", "explain", "tell me about", "define", "meaning of",
            "why do", "why does", "what are", "how do", "what causes", "history of",
            "science", "medicine", "technology", "politics", "geography", "math",
            "physics", "chemistry", "biology", "health", "disease", "treatment",
            "symptoms", "economy", "finance", "history", "culture", "religion",
            "philosophy", "psychology", "sociology", "anthropology", "literature",
            "art", "music", "film", "sports", "food", "travel", "language"
        ]

        # Check if this might be an out-of-scope action request
        if any(indicator in message for indicator in out_of_scope_action_indicators):
            # Always include limitations for potentially out-of-scope action requests
            relevant_sections.append("limitations")

            # Also include capabilities to show what the app CAN do
            relevant_sections.append("capabilities")

        # If it's a general knowledge question, don't include any app documentation
        # This will allow the LLM to use its built-in knowledge to answer
        is_general_knowledge = any(indicator in message.lower() for indicator in general_knowledge_indicators)
        if is_general_knowledge and not any(keyword in message.lower() for keyword in ["task", "todo", "priority", "due date", "app"]):
            # Return an empty list to indicate this is a general knowledge question
            # and doesn't need app documentation
            return []

        # Check if this is a general question about the app
        general_question_indicators = [
            "what is", "how do i", "what does", "explain", "tell me about",
            "what are", "how can", "what can", "help me understand", "meaning of",
            "definition of", "define", "mean by", "means", "meant by",
            "can you", "are you able", "is it possible", "do you have", "feature"
        ]

        is_general_question = any(indicator in message for indicator in general_question_indicators)

        if is_general_question:
            # Find relevant sections based on keywords
            for section, keywords in self.section_keywords.items():
                if any(keyword in message for keyword in keywords):
                    if section not in relevant_sections:  # Avoid duplicates
                        relevant_sections.append(section)

            # If asking about general capabilities, include that section
            if "what" in message and any(term in message for term in ["can you do", "can you help", "can you perform", "all can you"]):
                if "capabilities" not in relevant_sections:
                    relevant_sections.append("capabilities")

            # If asking what the app can't do, include limitations
            if any(term in message for term in ["can't", "cannot", "not able", "unable", "don't", "doesn't", "won't", "limitations", "limits"]):
                if "limitations" not in relevant_sections:
                    relevant_sections.append("limitations")

        return relevant_sections

    def get_documentation(self, section_names=None):
        """
        Get documentation content for specified sections.

        Args:
            section_names (list, optional): List of section names to retrieve.
                                          If None, returns all documentation.

        Returns:
            str: Combined documentation text
        """
        if not section_names:
            # If no specific sections requested, return empty string
            return ""

        docs = []
        for section in section_names:
            if section in self.documentation_sections:
                docs.append(self.documentation_sections[section])

        return "\n\n".join(docs)
