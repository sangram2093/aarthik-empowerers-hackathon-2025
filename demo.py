"""
Basic LLM Agent Example - Weather Assistant

This example demonstrates how to create a simple LLM agent that can:
1. Check weather for any city
2. Perform mathematical calculations
3. Respond to natural language queries

The agent uses the Gemini model to decide which tool to call based on user input.
"""

import sys
import os
from typing import Dict, Any

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import GOOGLE_API_KEY, DEFAULT_MODEL, validate_required_config
from utils.session_helpers import validate_config

import google.generativeai as genai
from google.adk.agents import LlmAgent
from empower_agent.agent import root_agent
# Configure Google AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_weather(city: str) -> Dict[str, Any]:
    """
    Gets the current weather for a city.
    
    This is a mock implementation that returns simulated weather data.
    In a real application, you would integrate with a weather API.
    
    Args:
        city: The name of the city to get weather for.
        
    Returns:
        A dictionary with weather information including temperature, 
        condition, and humidity.
    """
    # Mock weather data - in reality, you'd call a weather API
    import random
    
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Snowy"]
    temperature = random.randint(10, 30)
    condition = random.choice(conditions)
    humidity = random.randint(40, 80)
    
    return {
        "status": "success",
        "city": city,
        "temperature": f"{temperature}°C",
        "condition": condition,
        "humidity": f"{humidity}%",
        "description": f"The weather in {city} is {condition.lower()} with a temperature of {temperature}°C and {humidity}% humidity."
    }

def calculate_math(expression: str) -> Dict[str, Any]:
    """
    Performs mathematical calculations.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "15 * 8")
        
    Returns:
        A dictionary with the calculation result or error information.
    """
    try:
        # Simple evaluation - in production, use a safer math parser
        result = eval(expression)
        return {
            "status": "success",
            "expression": expression,
            "result": result,
            "description": f"The result of {expression} is {result}"
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "error": str(e),
            "description": f"Error calculating {expression}: {str(e)}"
        }

def get_time_info(timezone: str = "UTC") -> Dict[str, Any]:
    """
    Gets current time information.
    
    Args:
        timezone: The timezone to get time for (default: UTC)
        
    Returns:
        A dictionary with current time information.
    """
    from datetime import datetime
    import pytz
    
    try:
        if timezone.upper() == "UTC":
            tz = pytz.UTC
        else:
            tz = pytz.timezone(timezone)
        
        current_time = datetime.now(tz)
        
        return {
            "status": "success",
            "timezone": timezone,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "day_of_week": current_time.strftime("%A"),
            "description": f"The current time in {timezone} is {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ({current_time.strftime('%A')})"
        }
    except Exception as e:
        return {
            "status": "error",
            "timezone": timezone,
            "error": str(e),
            "description": f"Error getting time for {timezone}: {str(e)}"
        }



def demo_assistant():
    """
    Demonstrates the weather assistant with example queries.
    """
    from utils.session_helpers import ADKSessionManager, print_session_info
    
    print("🌤️  Weather Assistant Demo")
    print("=" * 50)
    
    # Create the agent
    try:
        agent = root_agent
        print("✅ Weather assistant created successfully!")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return
    
    # Create session manager
    session_manager = ADKSessionManager(app_name="empower app demo")
    runner = session_manager.create_runner(agent)
    
    # Print session info
    print_session_info(session_manager)
    
    # Example queries
    example_queries = [
        "Give me financial assistance",
        # "Calculate 25 * 4 + 10",
        # "What time is it in New York?",
        # "How's the weather in London?",
        # "What's 100 divided by 5?",
        # "What time is it in UTC?"
    ]
    
    print("Running example queries:")
    print("-" * 30)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: {query}")
        try:
            response = session_manager.run_query(query)
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed! Try running your own queries.")

if __name__ == "__main__":
    demo_assistant() 