import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in environment variables")
    exit(1)

# List models endpoint
LIST_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Make API request
response = requests.get(
    f"{LIST_MODELS_URL}?key={GEMINI_API_KEY}",
    headers={"Content-Type": "application/json"}
)

# Check if request was successful
if response.status_code == 200:
    models = response.json()
    print("Available models:")
    for model in models.get("models", []):
        print(f"- {model.get('name')}")
        print(f"  Display name: {model.get('displayName')}")
        print(f"  Description: {model.get('description')}")
        print(f"  Supported generation methods: {model.get('supportedGenerationMethods')}")
        print()
else:
    print(f"Error: {response.status_code} - {response.text}")
