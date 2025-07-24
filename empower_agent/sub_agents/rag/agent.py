
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from empower_agent.sub_agents.rag import prompt

rag_agent = Agent(
    model="gemini-2.5-flash",
    name="rag_agent",
    description="Given the matching information it creates the answer.",
    instruction=prompt.RAG_AGENT_INSTR,
    # tools=[
    #     AgentTool(agent=create_reservation),
    #     AgentTool(agent=payment_choice),
    #     AgentTool(agent=process_payment),
    # ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)