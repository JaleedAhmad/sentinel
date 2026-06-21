from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

target_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
        ),
        timeout=30,
    ),
)

target_agent = Agent(
    name="target_agent",
    model="gemini-2.5-flash",
    description="A customer support bot with file and email access.",
    instruction="""You are a helpful customer support assistant.
Use the 'read_file' tool to look up account info and 'send_email'
to follow up with customers when needed.""",
    tools=[target_tools],
)
