import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

# from agents.airbnb_planner_multiagent.internet_search.internet_search_agent import (
#     InternetSearchAgent,
# )
from is_search_agent import (
    create_is_agent,
)

from internet_search_agent_executor import (
    ISAgentExecutor,
)

# from agents.airbnb_planner_multiagent.internet_search.is_agent_executor import (
#     InternetSearchAgentExecutor as ISAgentExecutor,
# )
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


load_dotenv()

logging.basicConfig()

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 10003


def fetch_agent_card(host: str, port: int) -> AgentCard:
    """Fetch the agent card for the Internet Search Agent."""
    skill = AgentSkill(
        id="internet_search",
        name="Search internet",
        description="Helps with general queries by searching the internet.",
        tags=["internet", "search", "general"],
        examples=["who is PM of India?", "Latest news on AI"],
    )

    agent_card = AgentCard(
        name="Internet Agent",
        description="Helps with Internet queries by searching the internet.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    return agent_card


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    # Verify an API key is set.
    # Not required if using Vertex AI APIs.
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") != "TRUE" and not os.getenv(
        "GOOGLE_API_KEY"
    ):
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set and "
            "GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
        )

    skill = AgentSkill(
        id="internet_search",
        name="Search internet",
        description="Helps with general queries by searching the internet.",
        tags=["internet", "search", "general"],
        examples=["who is PM of India?", "Latest news on AI"],
    )

    agent_card = AgentCard(
        name="Internet Agent",
        description="Helps with Internet queries by searching the internet.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    adk_agent = create_is_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    agent_executor = ISAgentExecutor(runner, card=agent_card)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    uvicorn.run(a2a_app.build(), host=host, port=port)


@click.command()
@click.option("--host", "host", default=DEFAULT_HOST)
@click.option("--port", "port", default=DEFAULT_PORT)
def cli(host: str, port: int):
    main(host, port)


if __name__ == "__main__":
    main()
