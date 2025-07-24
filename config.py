# Demo.py will use this file.
"""
Centralized configuration for ADK samples.

This module provides configuration settings that are shared across all sample projects.
It handles environment variables, default values, and provides helper functions for
common configuration tasks.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API Configuration
# =============================================================================

# Google AI API Key (required)
GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

# Default model configuration
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "gemini-1.5-flash")

# =============================================================================
# Application Configuration
# =============================================================================

# Default application settings
DEFAULT_APP_NAME: str = os.getenv("DEFAULT_APP_NAME", "adk_samples_comprehensive")
DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "sample_user")
DEFAULT_SESSION_ID: str = os.getenv("DEFAULT_SESSION_ID", "sample_session")

# =============================================================================
# Retry and Error Handling Configuration
# =============================================================================

# Retry configuration
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
BACKOFF_MULTIPLIER: float = float(os.getenv("BACKOFF_MULTIPLIER", "2.0"))

# Timeout configuration (in seconds)
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
LONG_TIMEOUT: int = int(os.getenv("LONG_TIMEOUT", "120"))

# =============================================================================
# Logging Configuration
# =============================================================================

# Logging level
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("adk_samples.log", mode="a")
    ]
)

# =============================================================================
# Sample-Specific Configuration
# =============================================================================

# Weather API configuration (for weather samples)
WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
DEFAULT_WEATHER_CITY: str = os.getenv("DEFAULT_WEATHER_CITY", "San Francisco")

# News API configuration (for news samples)
NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
DEFAULT_NEWS_CATEGORY: str = os.getenv("DEFAULT_NEWS_CATEGORY", "technology")

# Stock API configuration (for financial samples)
STOCK_API_KEY: Optional[str] = os.getenv("STOCK_API_KEY")
DEFAULT_STOCK_SYMBOL: str = os.getenv("DEFAULT_STOCK_SYMBOL", "GOOGL")

# =============================================================================
# Development and Testing Configuration
# =============================================================================

# Development mode
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
VERBOSE_LOGGING: bool = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"

# Testing configuration
TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
MOCK_EXTERNAL_APIS: bool = os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true"

# =============================================================================
# Helper Functions
# =============================================================================

def get_session_config(app_name: Optional[str] = None, 
                      user_id: Optional[str] = None, 
                      session_id: Optional[str] = None) -> Dict[str, str]:
    """
    Get session configuration with optional overrides.
    
    Args:
        app_name: Optional app name override
        user_id: Optional user ID override
        session_id: Optional session ID override
        
    Returns:
        Dictionary with session configuration
    """
    return {
        "app_name": app_name or DEFAULT_APP_NAME,
        "user_id": user_id or DEFAULT_USER_ID,
        "session_id": session_id or DEFAULT_SESSION_ID
    }

def get_model_config(model: Optional[str] = None) -> Dict[str, Any]:
    """
    Get model configuration with optional override.
    
    Args:
        model: Optional model name override
        
    Returns:
        Dictionary with model configuration
    """
    return {
        "model": model or DEFAULT_MODEL,
        "fallback_model": FALLBACK_MODEL,
        "timeout": DEFAULT_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY
    }

def get_retry_config() -> Dict[str, Any]:
    """
    Get retry configuration.
    
    Returns:
        Dictionary with retry configuration
    """
    return {
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "backoff_multiplier": BACKOFF_MULTIPLIER,
        "timeout": DEFAULT_TIMEOUT
    }

def validate_required_config() -> bool:
    """
    Validate that required configuration is available.
    
    Returns:
        True if all required configuration is present, False otherwise
    """
    missing_config = []
    
    if not GOOGLE_API_KEY:
        missing_config.append("GOOGLE_API_KEY")
    
    if missing_config:
        logger = logging.getLogger(__name__)
        logger.error(f"Missing required configuration: {', '.join(missing_config)}")
        return False
    
    return True

def get_api_keys() -> Dict[str, Optional[str]]:
    """
    Get all configured API keys.
    
    Returns:
        Dictionary with all API keys (values may be None if not configured)
    """
    return {
        "google_ai": GOOGLE_API_KEY,
        "weather": WEATHER_API_KEY,
        "news": NEWS_API_KEY,
        "stock": STOCK_API_KEY
    }

def is_development_mode() -> bool:
    """
    Check if running in development mode.
    
    Returns:
        True if in development mode, False otherwise
    """
    return DEBUG_MODE or VERBOSE_LOGGING

def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration.
    
    Returns:
        Dictionary with logging configuration
    """
    return {
        "level": LOG_LEVEL,
        "format": LOG_FORMAT,
        "debug_mode": DEBUG_MODE,
        "verbose": VERBOSE_LOGGING
    }

def print_config_summary() -> None:
    """Print a summary of the current configuration."""
    print("\n" + "="*60)
    print("ADK SAMPLES CONFIGURATION SUMMARY")
    print("="*60)
    print(f"Model: {DEFAULT_MODEL}")
    print(f"App Name: {DEFAULT_APP_NAME}")
    print(f"User ID: {DEFAULT_USER_ID}")
    print(f"Session ID: {DEFAULT_SESSION_ID}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Debug Mode: {DEBUG_MODE}")
    print(f"Test Mode: {TEST_MODE}")
    print(f"Max Retries: {MAX_RETRIES}")
    print(f"Timeout: {DEFAULT_TIMEOUT}s")
    
    # API Keys status
    api_keys = get_api_keys()
    print("\nAPI Keys Status:")
    for key_name, key_value in api_keys.items():
        status = "✓ Configured" if key_value else "✗ Not configured"
        print(f"  {key_name.replace('_', ' ').title()}: {status}")
    
    print("="*60 + "\n")

# =============================================================================
# Environment Validation
# =============================================================================

def check_environment() -> bool:
    """
    Perform a comprehensive environment check.
    
    Returns:
        True if environment is properly configured, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check required configuration
    if not validate_required_config():
        return False
    
    # Check Python version
    import sys
    if sys.version_info < (3, 9):
        logger.error("Python 3.9 or higher is required")
        return False
    
    # Check required packages
    try:
        import google.generativeai
        import google.adk
    except ImportError as e:
        logger.error(f"Required package not found: {e}")
        return False
    
    logger.info("Environment check passed")
    return True

# =============================================================================
# Configuration Export
# =============================================================================

# Export commonly used configuration for easy import
__all__ = [
    # API Configuration
    "GOOGLE_API_KEY",
    "DEFAULT_MODEL",
    "FALLBACK_MODEL",
    
    # Application Configuration
    "DEFAULT_APP_NAME",
    "DEFAULT_USER_ID",
    "DEFAULT_SESSION_ID",
    
    # Retry Configuration
    "MAX_RETRIES",
    "RETRY_DELAY",
    "BACKOFF_MULTIPLIER",
    "DEFAULT_TIMEOUT",
    
    # Helper Functions
    "get_session_config",
    "get_model_config",
    "get_retry_config",
    "validate_required_config",
    "check_environment",
    "print_config_summary",
    
    # Development
    "DEBUG_MODE",
    "TEST_MODE",
    "is_development_mode"
] 