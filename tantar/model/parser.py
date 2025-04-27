from datetime import datetime
from schemas.model import (
    JuridicEvents,
    Event,
    FileMetadata,
    Person,
    PhysicalPersonModel,
    MoralPersonModel,
)
from typing import List, Optional, Tuple
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from enum import Enum
from pydantic import BaseModel, Field

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


class RelationShip(Enum):
    PRESIDENT = "PRESIDENT"
    DIRECTOR = "DIRECTOR"
    FOUNDER = "FOUNDER"
    ASSOCIATE = "ASSOCIATE"
    UNKNOW = "UNKNOW"


class RelationShipModel(BaseModel):
    date: Optional[str] = Field(
        description="The date of the relationship", default=None
    )
    source: Person = Field(description="The person who is in the relationship")
    target: MoralPersonModel = Field(
        description="The company which is in the relationship"
    )
    relationship: RelationShip = Field(
        description="The relationship between the person and the company"
    )


class Share(BaseModel):
    person: Person = Field(description="The person who owns the shares")
    shares: int = Field(description="The number of shares owned by the person")
    percentage: float = Field(
        description="The percentage of shares owned by the person"
    )


class ContractParties(BaseModel):
    offeree: Person = Field(description="The offeree of the contract")
    offeror: Person = Field(description="The offeror of the contract")


contract_party_agent = Agent(
    "openai:gpt-4o",
    result_type=ContractParties,
)


extract_relationship_agent = Agent(
    "openai:gpt-4o",
    result_type=List[RelationShipModel],
)

extract_shares_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Share],
)


async def extract_shares(pages: List[str]) -> List[Share]:
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


async def extract_relationships(pages: List[str]) -> List[RelationShipModel]:
    history = [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="Extract the relationships",
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
    message = await extract_relationship_agent.run("END", message_history=history)
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
    return message.data.events


async def extract_persons(event: Event) -> List[Person]:
    message = await persons_agent.run(f"Extract the persons in this text: {event.text}")
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
