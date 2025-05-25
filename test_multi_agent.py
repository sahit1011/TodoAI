#!/usr/bin/env python3
"""
Test script for the multi-agent system.

This script tests the multi-agent system by simulating user messages and checking the responses.
"""

import os
import sys
import logging
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules
from backend.database import SessionLocal, engine, Base
from backend.models.user import User
from backend.models.task import Task
from backend.agent.multi_agent_process import multi_agent_process

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to test the multi-agent system."""
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Get or create a test user
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Initialize conversation context
        conversation_context = []
        
        # Test messages
        test_messages = [
            "Hi, how are you today?",
            "Create a task called 'Test the multi-agent system' with high priority",
            "Show me all my tasks",
            "Mark the task 'Test the multi-agent system' as complete",
            "Delete the task 'Test the multi-agent system'",
            "What can you help me with?"
        ]
        
        # Process each test message
        for message in test_messages:
            print(f"\n--- Testing message: {message} ---")
            
            # Process the message
            response, actions = multi_agent_process(message, conversation_context, user, db)
            
            # Print the response and actions
            print(f"Response: {response}")
            print(f"Actions: {actions}")
            
            # Print the updated conversation context
            print(f"Conversation context: {conversation_context[-1]}")
    
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")
    
    finally:
        # Close the database session
        db.close()

if __name__ == "__main__":
    main()
