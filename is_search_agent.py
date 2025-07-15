from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


def create_is_agent() -> LlmAgent:
    """Constructs the ADK agent."""
    return LlmAgent(
        model="gemini-2.5-flash-preview-04-17",
        name="internet_search_agent",
        description="An agent that can help answer general queries after searching them on internet using the tool provided.",
        instruction="""You are an Internet Search Agent. Use the tools provided to answer general queries that are not in your domain. If you cannot find an answer, provide a general response. You must rely exclusively on these tools for data and refrain from inventing information. Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. If no response is received from the tool, clearly state that the tool is unable to process the request. Never make up information or provide answers without using the tools.""",
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command="python",
                    args=["./internet_search_mcp.py"],
                ),
            )
        ],
    )
