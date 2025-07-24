
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from empower_agent.sub_agents.agricultural import prompt
from empower_agent.sub_agents.agricultural.tools import (
    get_geolocation_data,
    get_current_season,
    get_environmental_data,
    get_indian_crop_recommendations,
    get_livestock_recommendations,
    get_recommendations_for_current_season
)

agricultural_agent = Agent(
    model="gemini-2.5-flash",
    name="agricultural_agent",
    description="Given the place it provides the farming related advice",
    instruction=prompt.AGRICULTURAL_AGENT_INSTR,
    tools=[get_geolocation_data, get_current_season, get_environmental_data, get_indian_crop_recommendations, get_livestock_recommendations, get_recommendations_for_current_season],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)