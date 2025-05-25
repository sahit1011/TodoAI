#!/bin/bash

# Hardcoded token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc0NDQwODQ3Mn0.hW9PYGhLPzX5XAC7ieVeMcdqjmyeOBZBcjRHN2u_dvc"

echo "Testing API with hardcoded token..."
echo "Token: $TOKEN"
echo

echo "1. Fetching tasks..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
echo

echo "2. Creating a new task..."
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"title": "API Test Task", "description": "Created from API test script", "priority": "high"}' http://localhost:8000/api/tasks
echo

echo "3. Fetching tasks again..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
echo

echo "API test completed!"
