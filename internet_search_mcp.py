from mcp.server.fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
import concurrent.futures
import time
import traceback
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_exa import ExaSearchResults
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
# Create a new MCP server
mcp = FastMCP(
    name="internet_search",
    version="1.0.0",
    description="Provides out of domain handling for general queries",
)


@mcp.tool(
    name="resilient_search",
    description="Search using fallback chain: DuckDuckGo → Tavily → Serper → Exa.",
)
def resilient_search(query: str) -> str:
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API")
    SERP_API = os.getenv("SERP_API")
    # EXA_API = os.getenv("EXA_API")
    timeout = 5
    logging.info(f"🔍 inside resilient tool, Searching for: {query}")

    def try_with_timeout(func, query):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, query)
            return future.result(timeout=timeout)

    tools = [
        ("DuckDuckGo", lambda q: DuckDuckGoSearchRun().run(q)),
        ("Serper", lambda q: GoogleSerperAPIWrapper(serper_api_key=SERP_API).run(q)),
        (
            "Tavily",
            lambda q: TavilySearch(max_results=2, topic="general").invoke({"query": q})[
                "results"
            ][0]["content"],
        ),
    ]

    for name, func in tools:
        try:
            logging.info(f"🔍 Trying {name}...")
            start = time.time()
            result = try_with_timeout(func, query)
            elapsed = round(time.time() - start, 2)
            logging.info(f"✅ {name} succeeded in {elapsed}s.")
            return result
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            print(traceback.format_exc())

    logging.error("❌ All tools failed. Please try again later.")
    return "❌ All tools failed. Please try again later."


# @mcp.tool(name="duckduckgo", description="Free web search using DuckDuckGo")
# def duck_duck_go(query: str) -> str:
#     """Searching the web using DuckDuckGo."""
#     # with DDGS() as ddgs:
#     #     results = ddgs.text(query, max_results=3)
#     #     print("results", results)
#     #     return [r["body"] for r in results]
#     duckduckgo = DuckDuckGoSearchRun()
#     results = duckduckgo.run(query)
#     print("results", results)
#     return results


# @mcp.tool(name="tavily", description="Premium web search using Tavily")
# def tavily_search(query: str) -> str:
#     """Searching the web using Tavily."""
#     try:
#         tavily = TavilySearch(max_results=3)
#         results = tavily.invoke({"query": query})
#         print("tavily results", results, flush=True)
#         return results
#     except Exception as e:
#         print("Tavily tool failed:", e, flush=True)
#         return "Tavily failed to return results"


if __name__ == "__main__":
    logging.info("Starting the Internet Search MCP server...")
    # mcp.run(transport="sse")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logging.error(f"Error running MCP server: {e}")
        traceback.print_exc()
