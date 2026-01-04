from datetime import datetime
from schemas.objects import Event, Person, FileMetadata, ContractParties, Shares
from schemas.relational import RoleName
from typing import List
from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

extract_events_template = """
Extract the events in this document using this description:
{format_instructions}

Only extract the "Décisions" or the "Résolutions" the paragraph should start with one of those word, if it is not the case ignore it.
"""


events_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Event],
)

document_information_agent = Agent(
    "openai:gpt-4o",
    result_type=FileMetadata,
)

persons_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Person],
)


contract_party_agent = Agent(
    "openai:gpt-4o",
    result_type=ContractParties,
)


extract_shares_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Shares],
)


class PersonRole(BaseModel):
    role: RoleName = Field(description="The role of the person")
    person: Person = Field(description="The person with the role")


extract_roles_agent = Agent(
    "openai:gpt-4o",
    result_type=List[PersonRole],
)


async def extract_shares(pages: List[str]) -> List[Shares]:
    logger.info("LLM extract_shares start page_count=%s", len(pages))
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the shares",
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
    message = await extract_shares_agent.run("END", message_history=history)
    share_count = len(message.data) if message.data else 0
    logger.info("LLM extract_shares done share_count=%s", share_count)
    return message.data


async def extract_document_metadata(pages: List[str]) -> FileMetadata:
    logger.info("LLM extract_document_metadata start page_count=%s", len(pages))
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the document information. If the document is a contract, you may encounter multiple sirens and company names, please pick the offeree and not the offeror.",
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
    message = await document_information_agent.run("END", message_history=history)
    logger.info(
        "LLM extract_document_metadata done name=%s siren=%s type=%s",
        message.data.name,
        message.data.siren,
        message.data.type,
    )
    return message.data


async def extract_events(pages: List[str]) -> List[Event]:
    logger.info("LLM extract_events start page_count=%s", len(pages))
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
    event_count = len(message.data) if message.data else 0
    logger.info("LLM extract_events done event_count=%s", event_count)
    return message.data


async def extract_persons(text: str) -> List[Person]:
    logger.info("LLM extract_persons start text_len=%s", len(text))
    message = await persons_agent.run(f"Extract the persons in this text: {text}")
    person_count = len(message.data) if message.data else 0
    logger.info("LLM extract_persons done person_count=%s", person_count)
    return message.data


async def extract_contract_parties(pages: List[str]) -> ContractParties:
    logger.info("LLM extract_contract_parties start page_count=%s", len(pages))
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the offeror person from the contract",
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
    message = await contract_party_agent.run("END", message_history=history)
    logger.info("LLM extract_contract_parties done")
    return message.data


async def extract_roles(pages: List[str]) -> List[PersonRole]:
    logger.info("LLM extract_roles start page_count=%s", len(pages))
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the roles of the persons in this document",
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
    message = await extract_roles_agent.run("END", message_history=history)
    role_count = len(message.data) if message.data else 0
    logger.info("LLM extract_roles done role_count=%s", role_count)
    return message.data
