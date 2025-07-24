
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from empower_agent.sub_agents.agricultural import prompt

agricultural_agent = Agent(
    model="gemini-2.5-flash",
    name="agricultural_agent",
    description="Given the place it provides the farming related advice",
    instruction=prompt.BOOKING_AGENT_INSTR,
    # tools=[
    #     AgentTool(agent=create_reservation),
    #     AgentTool(agent=payment_choice),
    #     AgentTool(agent=process_payment),
    # ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)