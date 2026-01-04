from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from typing import List, Optional
from schemas.objects import Event, Person
from schemas.file_model import (
    EventTypeModel,
    ContractTypeModel,
    FileTypeModel,
    ContractType,
    FileType,
)
from datetime import datetime
from tantar.utils.logger import get_logger

logger = get_logger(__name__)


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
    logger.info("LLM classify_file start page_count=%s", len(pages))
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
    logger.info("LLM classify_file done type=%s", result.data.type)
    return result.data.type


async def classify_contract(pages: List[str]) -> ContractType:
    logger.info("LLM classify_contract start page_count=%s", len(pages))
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
    logger.info("LLM classify_contract done type=%s", result.data.type)
    return result.data.type


async def classify_juridic_event(event: Event) -> EventTypeModel:
    event_id = getattr(event, "original_id", None) or getattr(event, "id", None)
    logger.info("LLM classify_juridic_event start event_id=%s", event_id)
    result = await event_classifier_agent.run(
        f'Classify the event "{event.title}" "{event.text}"'
    )
    logger.info("LLM classify_juridic_event done event_id=%s result=%s", event_id, result.data)
    return result.data


async def classify_person_exists(name: str, persons: List[Person]) -> Optional[str]:
    logger.info(
        "LLM classify_person_exists start name=%s person_count=%s",
        name,
        len(persons),
    )
    result = await person_exists_agent.run(
        f'Within the context of the following persons: {", ".join([f"name: {person.name} id: {person.original_id}" for person in persons])}, does the person "{name}" exist? if yes, return the id of the person, if no, return None'
    )
    logger.info("LLM classify_person_exists done name=%s result=%s", name, result.data)
    return result.data
