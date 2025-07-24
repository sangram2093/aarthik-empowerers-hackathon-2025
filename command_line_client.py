from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from empower_agent.agent import root_agent
import asyncio
import time
load_dotenv()

def greet_user(name: str) -> str:
    return f"Hello, {name}!"

my_agent = Agent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    description="An agent that can greet users.",
    instruction="You are a friendly assistant that greets users.",
    tools=[greet_user]
)

# 2. Set up the Session Service and Runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,  # Use the root agent defined in empower_agent/agent.py
    app_name="my_adk_app",
    session_service=session_service,
)

# 3. Define an async function to interact with the agent
async def interact_with_agent(user_query: str):
    """Sends a query to the agent and prints the final response."""

    print(f"\nYou: {user_query}")

    # Create content from the user query
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_query)]
    )

    #  Initialize or retrieve the session
    session_id = "my_session"
    await session_service.create_session(
        app_name="my_adk_app", user_id="user_123", session_id=session_id
    ) # Creating a session for each interaction

    # Run the agent asynchronously and iterate through the events
    async for event in runner.run_async(
        user_id="user_123",
        session_id=session_id,
        new_message=user_content
    ):
        # Inspect each event
        if event.is_final_response():
            # Check if the event contains content and parts before accessing
            if event.content and event.content.parts: 
                final_response_text = event.content.parts[0].text
                print(f"\nAgent: {final_response_text}")
            else:
                print("\nAgent: Received a final response without readable content.")
        # You can add more checks here to handle different event types
        # For example, tool calls, intermediate thoughts, etc.
        # See ADK documentation for various event types and their attributes.


# 4. Run the interaction
async def main():
    await interact_with_agent("Which crop is best for this season in pune?")

if __name__ == "__main__":
    asyncio.run(main())