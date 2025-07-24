"""
Session management utilities for ADK samples.

This module provides helper functions for creating and managing ADK sessions
in a consistent way across all examples.
"""

import sys
import os
from typing import Optional, Dict, Any
import logging

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GOOGLE_API_KEY, DEFAULT_MODEL, DEFAULT_APP_NAME, 
    DEFAULT_USER_ID, DEFAULT_SESSION_ID, get_session_config, get_model_config
)

import google.generativeai as genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger(__name__)

class ADKSessionManager:
    """
    Manages ADK sessions and provides convenient methods for agent execution.
    """
    
    def __init__(self, app_name: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize the session manager.
        
        Args:
            app_name: Optional app name override
            user_id: Optional user ID override
        """
        self.app_name = app_name or DEFAULT_APP_NAME
        self.user_id = user_id or DEFAULT_USER_ID
        self.session_id = DEFAULT_SESSION_ID
        
        # Configure Google AI
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
        else:
            logger.warning("GOOGLE_API_KEY not set. Some functionality may not work.")
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        self.session = None
        self.runner = None
        
        self._create_session()
    
    async def _create_session(self) -> None:
        """Create a new session."""
        try:
            self.session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id
            )
            logger.info(f"Created session: {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def create_runner(self, agent) -> Runner:
        """
        Create a runner for the given agent.
        
        Args:
            agent: The ADK agent to create a runner for
            
        Returns:
            Runner instance
        """
        try:
            self.runner = Runner(
                agent=agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            logger.info(f"Created runner for agent: {agent.name}")
            return self.runner
        except Exception as e:
            logger.error(f"Failed to create runner: {e}")
            raise
    
    def run_query(self, query: str, runner: Optional[Runner] = None) -> str:
        """
        Run a query using the specified runner.
        
        Args:
            query: The query string to process
            runner: Optional runner instance (uses self.runner if not provided)
            
        Returns:
            The final response from the agent
        """
        if runner is None:
            runner = self.runner
        
        if runner is None:
            raise ValueError("No runner available. Call create_runner() first.")
        
        try:
            # Create content from user query
            content = types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
            
            # Run the agent
            events = runner.run(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=content
            )
            
            # Process events to get the final response
            for event in events:
                if event.is_final_response():
                    return event.content.parts[0].text
            
            return "No response received."
            
        except Exception as e:
            logger.error(f"Error running query: {e}")
            return f"Error: {str(e)}"

def create_simple_session(agent, app_name: Optional[str] = None) -> ADKSessionManager:
    """
    Create a simple session manager with a runner for the given agent.
    
    Args:
        agent: The ADK agent
        app_name: Optional app name override
        
    Returns:
        Configured ADKSessionManager instance
    """
    session_manager = ADKSessionManager(app_name=app_name)
    session_manager.create_runner(agent)
    return session_manager

def run_simple_query(agent, query: str, app_name: Optional[str] = None) -> str:
    """
    Run a simple query with an agent using default session settings.
    
    Args:
        agent: The ADK agent
        query: The query string
        app_name: Optional app name override
        
    Returns:
        The agent's response
    """
    session_manager = create_simple_session(agent, app_name)
    return session_manager.run_query(query)

def validate_config() -> bool:
    """
    Validate that the required configuration is available.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY is not set")
        print("Error: GOOGLE_API_KEY is not set. Please set it in your .env file or environment variables.")
        return False
    
    return True

def print_session_info(session_manager: ADKSessionManager) -> None:
    """
    Print session information for debugging purposes.
    
    Args:
        session_manager: The session manager instance
    """
    print("\n" + "="*50)
    print("SESSION INFORMATION")
    print("="*50)
    print(f"App Name: {session_manager.app_name}")
    print(f"User ID: {session_manager.user_id}")
    print(f"Session ID: {session_manager.session_id}")
    print(f"Model: {DEFAULT_MODEL}")
    print("="*50 + "\n") 