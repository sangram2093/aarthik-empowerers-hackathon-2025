from google.adk.agents import Agent

from empower_agent import prompt

from empower_agent.sub_agents.rag.agent import rag_agent
from empower_agent.sub_agents.agricultural.agent import agricultural_agent
from empower_agent.sub_agents.market_price.agent import market_price_agent

#todo check
from empower_agent.tools.memory import _load_precreated_itinerary


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A financial coach using services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        rag_agent,
        agricultural_agent,
        market_price_agent
    ],
    #todo 
    before_agent_callback=_load_precreated_itinerary,
)