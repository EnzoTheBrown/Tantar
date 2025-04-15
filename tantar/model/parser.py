from datetime import datetime
from schemas.model import JuridicEvents, Event, FileMetadata, Person
from typing import List
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart

extract_events_template = """
Extract the events in this document using this description:
{format_instructions}

Only extract the "Décisions" or the "Résolutions" the paragraph should start with one of those word, if it is not the case ignore it.
"""


events_agent = Agent(
    "openai:gpt-4o",
    result_type=JuridicEvents,
)

document_information_agent = Agent(
    "openai:gpt-4o",
    result_type=FileMetadata,
)

persons_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Person],
)


async def extract_document_metadata(pages: List[str]) -> FileMetadata:
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the document information",
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
                for page in pages[:2]
            ],
            kind="request",
        )
    ]
    message = await document_information_agent.run("END", message_history=history)
    return message.data


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
    return message.data.events


async def extract_persons(persons: List[Person], text: str) -> List[Person]:
    message = await persons_agent.run(
        f"Extract the persons in this text: {text}, if there is the person in that list return the extact name of the person: {persons}"
    )
    return message.data
