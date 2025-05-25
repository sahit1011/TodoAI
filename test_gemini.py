import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables")
    exit(1)

print(f"Using API key: {api_key[:10]}...")

# Configure Gemini API
genai.configure(api_key=api_key)

# List available models
print("\nListing available models:")
try:
    for m in genai.list_models():
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

# Test with Gemini Pro
print("\nTesting with Gemini Pro:")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, what can you do?")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error with Gemini Pro: {e}")

# Test with Gemini Pro 2.5
print("\nTesting with Gemini Pro 2.5:")
try:
    model = genai.GenerativeModel('gemini-pro-2.5')
    response = model.generate_content("Hello, what can you do?")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error with Gemini Pro 2.5: {e}")

print("\nTest completed.")
