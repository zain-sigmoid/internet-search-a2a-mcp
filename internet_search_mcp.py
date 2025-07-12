from mcp.server.fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

load_dotenv()
# Create a new MCP server
mcp = FastMCP(
    name="internet_search",
    version="1.0.0",
    description="Provides out of domain handling for general queries",
)
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API")


@mcp.tool(name="duckduckgo", description="Free web search using DuckDuckGo")
def duck_duck_go(query: str) -> str:
    """Searching the web using DuckDuckGo."""
    # with DDGS() as ddgs:
    #     results = ddgs.text(query, max_results=3)
    #     print("results", results)
    #     return [r["body"] for r in results]
    duckduckgo = DuckDuckGoSearchRun()
    results = duckduckgo.run(query)
    print("results", results)
    return results


@mcp.tool(name="tavily", description="Premium web search using Tavily")
def tavily_search(query: str) -> str:
    """Searching the web using Tavily."""
    try:
        tavily = TavilySearch(max_results=3)
        results = tavily.invoke({"query": query})
        print("tavily results", results, flush=True)
        return results
    except Exception as e:
        print("Tavily tool failed:", e, flush=True)
        return "Tavily failed to return results"


if __name__ == "__main__":
    # print("Starting the Internet Search MCP server...")
    # mcp.run(transport="sse")
    mcp.run(transport="stdio")
