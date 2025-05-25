import os
import json
from dotenv import load_dotenv
from backend.agent.simple_gemini import classify_intent

# Load environment variables
load_dotenv()

# Test the classify_intent function
def test_classify_intent():
    # Test with a simple message
    message = "Create a new task called 'Prepare presentation' with high priority"
    intent, parameters = classify_intent(message)
    
    print(f"Intent: {intent}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    # Test with another message
    message = "Show me all my tasks"
    intent, parameters = classify_intent(message)
    
    print(f"\nIntent: {intent}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    # Test with a more complex message
    message = "Mark the task about presentation as complete"
    intent, parameters = classify_intent(message)
    
    print(f"\nIntent: {intent}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")

if __name__ == "__main__":
    test_classify_intent()
