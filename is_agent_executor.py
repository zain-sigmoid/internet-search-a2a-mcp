# internet_search_agent_executor.py

import logging
from a2a.types import TaskState
from a2a.server.tasks import TaskUpdater
from google.adk import Runner
from a2a.types import (
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
)
from google.genai import types

from .internet_search_agent import (
    InternetSearchAgent,
)

logger = logging.getLogger(__name__)
DEFAULT_USER_ID = "user"


class InternetSearchAgentExecutor:
    def __init__(self, agent_name: str = "InternetSearchAgent", runner: Runner = None):
        self.agent_name = agent_name
        self.agent = None
        self.runner = runner
        self._active_sessions = set()

    async def init_agent(self):
        self.agent = InternetSearchAgent(agent_name=self.agent_name)
        await self.agent.init_agent()
        logger.info(
            f"{self.agent_name} initialized with tools: {[tool.name for tool in self.agent.tools]}"
        )

    async def _process_request(
        self,
        new_message,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id
        self._active_sessions.add(session_id)

        actual_agent = self.agent.agent  # ✅ the inner Gemini Agent, NOT the wrapper

        try:
            async for event in self.runner.run_async(
                session_id=session_id,
                user_id=DEFAULT_USER_ID,
                new_message=new_message,
                agent=actual_agent,  # ✅ Fixes the ValidationError
            ):
                if event.is_final_response():
                    parts = [
                        convert_genai_part_to_a2a(part)
                        for part in event.content.parts
                        if (part.text or part.file_data or part.inline_data)
                    ]
                    logger.debug("Yielding final response: %s", parts)
                    await task_updater.add_artifact(parts)
                    await task_updater.update_status(TaskState.completed, final=True)
                    break

                if not event.get_function_calls():
                    logger.debug("Yielding intermediate response")
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(
                            [
                                convert_genai_part_to_a2a(part)
                                for part in event.content.parts
                                if (part.text or part.file_data or part.inline_data)
                            ]
                        ),
                    )
                else:
                    logger.debug("Skipping event with tool call")
        finally:
            self._active_sessions.discard(session_id)

    async def execute(self, request, task_updater: TaskUpdater):
        try:
            await self._process_request(
                new_message=request.message,
                session_id=request.session_id,
                task_updater=task_updater,
            )
        except Exception as e:
            logger.exception("Execution failed")
            await task_updater.update_status(TaskState.failed, error_message=str(e))

    async def _upsert_session(self, session_id):
        return await self.runner.session_store.upsert(session_id=session_id)


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """Convert a single Google Gen AI Part type into an A2A Part type.

    Args:
        part: The Google Gen AI Part to convert

    Returns:
        The equivalent A2A Part

    Raises:
        ValueError: If the part type is not supported
    """
    if part.text:
        return TextPart(text=part.text)
    if part.file_data:
        return FilePart(
            file=FileWithUri(
                uri=part.file_data.file_uri,
                mime_type=part.file_data.mime_type,
            )
        )
    if part.inline_data:
        return Part(
            root=FilePart(
                file=FileWithBytes(
                    bytes=part.inline_data.data,
                    mime_type=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f"Unsupported part type: {part}")
