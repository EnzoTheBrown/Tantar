from datetime import datetime
from schemas.model import JuridicEvents, Event
from typing import List
from enum import Enum
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart

extract_events_template = """
Extract the events in this document using this description:
{format_instructions}

Only extract the "Décisions" or the "Résolutions" the paragraph should start with one of those word, if it is not the case ignore it.
"""


extract_file_information_template = """
Please extract the given information from this juridic document
{format_instructions}
"""


class EventType(Enum):
    DECISION = "Décision"
    RESOLUTION = "Résolution"


events_agent = Agent(
    "openai:gpt-4o",
    result_type=JuridicEvents,
)


async def extract_events(pages: List[str]) -> List[Event]:
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content=extract_events_template,
                    dynamic_ref=None,
                    part_kind="system-prompt",
                ),
            ]
            + [
                UserPromptPart(
                    content=page,
                    timestamp=datetime.now(),
                    part_kind="user-prompt",
                )
                for page in pages
            ],
            kind="request",
        )
    ]
    message = await events_agent.run("END", message_history=history)
    return message.data.juridic_events
