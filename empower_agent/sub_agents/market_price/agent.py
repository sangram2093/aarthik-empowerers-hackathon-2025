
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from empower_agent.sub_agents.market_price import prompt

market_price_agent = Agent(
    model="gemini-2.5-flash",
    name="market_price_agent",
    description="Given the place and crop it provides the local price of the crop.",
    instruction=prompt.MARKET_PRICE_AGENT_INSTR,
    # tools=[
    #     AgentTool(agent=create_reservation),
    #     AgentTool(agent=payment_choice),
    #     AgentTool(agent=process_payment),
    # ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)