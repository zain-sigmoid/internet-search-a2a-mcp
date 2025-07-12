import logging
import os

import click
import uvicorn
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.applications import Starlette

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from is_search_agent import create_is_agent
from internet_search_agent_executor import ISAgentExecutor

from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

load_dotenv()
logging.basicConfig()

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = int(os.getenv("PORT", 10003))


def fetch_agent_card(host: str, port: int) -> AgentCard:
    skill = AgentSkill(
        id="internet_search",
        name="Search internet",
        description="Helps with general queries by searching the internet.",
        tags=["internet", "search", "general"],
        examples=["who is PM of India?", "Latest news on AI"],
    )

    return AgentCard(
        name="Internet Agent",
        description="Helps with Internet queries by searching the internet.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )


def create_app(host: str, port: int):
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") != "TRUE" and not os.getenv(
        "GOOGLE_API_KEY"
    ):
        raise ValueError(
            "GOOGLE_API_KEY not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
        )

    agent_card = fetch_agent_card(host, port)
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

    # Add custom root endpoint
    async def root_endpoint(request):
        return JSONResponse(
            {
                "status": "success",
                "value": "Internet Search Agent is running",
                "version": 1.0,
            }
        )

    custom_routes = [
        Route("/", endpoint=root_endpoint, methods=["GET"]),
        Mount("/", app=a2a_app.build()),  # mounts POST route and others
    ]

    return Starlette(routes=custom_routes)


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    app = create_app(host, port)
    uvicorn.run(app, host=host, port=port)


@click.command()
@click.option("--host", default=DEFAULT_HOST)
@click.option("--port", default=DEFAULT_PORT)
def cli(host: str, port: int):
    main(host, port)


if __name__ == "__main__":
    main()
