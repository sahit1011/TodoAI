# LangChain Integration for Todo AI

This module provides integration with LangChain for handling out-of-scope requests like web searches, real-time data access, and other external services.

## Overview

The LangChain integration extends the Todo AI application with capabilities beyond task management. It allows the AI assistant to:

1. Search the web for information
2. Answer general knowledge questions
3. Access external services (future expansion)

## Architecture

The integration follows a hybrid approach:

1. **Core Task Management**: Handled by the existing Todo AI multi-agent system
2. **Out-of-Scope Requests**: Routed to the LangChain agent

The system uses a request router to determine which agent should handle each user request.

## Components

- **LangChainAgent**: Handles out-of-scope requests using LangChain tools
- **RequestRouter**: Routes requests to the appropriate agent system
- **Tools**: Web search, Wikipedia, etc.

## Configuration

The integration requires API keys for external services:

1. **OpenAI API Key**: Required for the LangChain LLM
2. **SerpAPI Key**: Optional for web search functionality

Set these in the `.env` file in the project root.

## Usage

The integration is automatically activated when a user asks for information or actions beyond the scope of task management. No special commands are needed.

Example requests that will be handled by LangChain:
- "What is the capital of France?"
- "How does photosynthesis work?"
- "Search for the latest news about AI"

## Extending

To add new tools to the LangChain agent:

1. Import the tool from LangChain or create a custom tool
2. Add it to the `_initialize_tools` method in `langchain_agent.py`
3. Update the `is_request_supported` method to detect requests for the new tool

## Limitations

- The LangChain integration requires an OpenAI API key
- Web search functionality requires a SerpAPI key
- The integration is designed for informational requests, not actions that modify external systems
