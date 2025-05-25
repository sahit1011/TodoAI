"""
Multi-Agent System for Todo AI

This package contains the implementation of a multi-agent system for the Todo AI application.
It includes a conversational agent for understanding user intent and an action agent for
executing database operations.
"""

from .coordinator import MultiAgentCoordinator

# Export the main coordinator class
__all__ = ['MultiAgentCoordinator']
