from google.adk.agents import Agent
from tools.mock_tools import read_file, send_email

target_agent = Agent(
    name="target_agent",
    model="gemini-2.5-flash",
    description="A customer support bot with file and email access.",
    instruction="""You are a helpful customer support assistant.
Use the 'read_file' tool to look up account info and 'send_email'
to follow up with customers when needed.""",
    tools=[read_file, send_email],
)
