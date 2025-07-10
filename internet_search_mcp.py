from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS

# Create a new MCP server
mcp = FastMCP(
    name="internet_search",
    version="1.0.0",
    description="Provides out of domain handling for general queries",
)


@mcp.tool(name="duckduckgo", description="Out of Domain Agent handling general queries")
def duck_duck_go(query: str) -> str:
    """Searching the web using DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        return [r["body"] for r in results]


if __name__ == "__main__":
    # print("Starting the Internet Search MCP server...")
    # mcp.run(transport="sse")
    mcp.run(transport="stdio")
