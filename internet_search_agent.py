from .utils import get_mcp_server_config
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.agents import Agent
from google.genai import types as genai_types
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InternetSearchAgent:
    def __init__(
        self,
        instructions: str = "You are an Internet Search Agent. Use the tools provided to answer general queries that are not in your domain. If you cannot find an answer, provide a general response.",
        agent_name: str = "Internet Search Agent",
        description: str = "Provides out of domain handling for general queries",
    ):
        self.agent_name = (agent_name,)
        self.description = (description,)
        self.content_types = ["text", "text/plain"]
        self.instructions = instructions

    async def init_agent(self):
        # ======================================
        # Initialize the MCP Toolset with the server configuration
        # ======================================
        config = get_mcp_server_config()
        tools = await MCPToolset(
            connection_params=SseServerParams(url=config.url)
        ).get_tools()

        for tool in tools:
            print(f"Tool loaded: {tool.name} - {tool.description}")
        generate_content_config = genai_types.GenerateContentConfig(temperature=0.0)
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model="gemini-2.0-flash",
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,
        )

    async def invoke(self, query, session_id) -> dict:
        logger.info(f"Running {self.agent_name} for session {session_id}")

        actual_agent = self.agent.agent
        if not hasattr(self, "agent") or actual_agent is None:
            await self.init_agent()

        try:
            # Run the agent on the user query
            result = await actual_agent.run(query)
            print(f"Result from agent: {result}")
            # If result is structured (e.g., from a tool), format it nicely
            if isinstance(result, dict):
                return {
                    "session_id": session_id,
                    "agent_name": self.agent_name,
                    "result": result,
                }
            else:
                return {
                    "session_id": session_id,
                    "agent_name": self.agent_name,
                    "result": str(result),
                }

        except Exception as e:
            logger.exception("Error while running agent")
            return {
                "session_id": session_id,
                "agent_name": self.agent_name,
                "error": str(e),
            }
