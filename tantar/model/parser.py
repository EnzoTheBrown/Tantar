from datetime import datetime
from schemas.objects import Event, Person, FileMetadata, ContractParties, Shares
from schemas.relational import RoleName
from typing import List, Tuple
from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart

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
    return message.data


async def extract_document_metadata(pages: List[str]) -> FileMetadata:
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
    return message.data


async def extract_persons(text: str) -> List[Person]:
    message = await persons_agent.run(f"Extract the persons in this text: {text}")
    return message.data


async def extract_contract_parties(pages: List[str]) -> ContractParties:
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
    return message.data


async def extract_roles(pages: List[str]) -> List[PersonRole]:
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
    return message.data
