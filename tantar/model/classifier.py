from pydantic_ai import Agent
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from enum import Enum
from typing import List
from schemas.model import FileMetadata, Contract
from datetime import datetime


class FileType(str, Enum):
    CONTRACT = "CONTRACT"
    PVAG = "Process Verbal Assemblée Générale"


file_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=FileMetadata,
)

contract_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=Contract,
)


async def classify_file(pages: List[str]) -> FileMetadata:
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
    return result.data


async def classify_contract(pages: List[str]) -> Contract:
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
    return result.data
