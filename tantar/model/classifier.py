from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from typing import List, Optional
from schemas.relational import Event, Person
from schemas.file_model import (
    EventTypeModel,
    ContractTypeModel,
    FileTypeModel,
    ContractType,
    FileType,
)
from datetime import datetime


file_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=FileTypeModel,
)

contract_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=ContractTypeModel,
)


event_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=EventTypeModel,
)

person_exists_agent = Agent(
    "openai:gpt-4o",
    result_type=Optional[str],
)


async def classify_file(pages: List[str]) -> FileType:
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Classify the file",
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
    result = await file_classifier_agent.run("END", message_history=history)
    return result.data.type


async def classify_contract(pages: List[str]) -> ContractType:
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Classify the contract",
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
                for page in pages[:5]
            ],
            kind="request",
        )
    ]
    result = await contract_classifier_agent.run("END", message_history=history)
    return result.data.type


async def classify_juridic_event(event: Event) -> EventTypeModel:
    result = await event_classifier_agent.run(
        f'Classify the event "{event.title}" "{event.text}"'
    )
    return result.data


async def classify_person_exists(name: str, persons: List[Person]) -> Optional[str]:
    result = await person_exists_agent.run(
        f'Within the context of the following persons: {", ".join([f"name: {person.name} id: {person.original_id}" for person in persons])}, does the person "{name}" exist? if yes, return the id of the person, if no, return None'
    )
    return result.data
