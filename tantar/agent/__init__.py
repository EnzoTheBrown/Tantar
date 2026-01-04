import asyncio
from pydantic import BaseModel, Field
from typing import Any, Optional, Self, Dict, List, Callable, Tuple
from pydantic_ai.messages import UserPromptPart, ModelRequest, SystemPromptPart
from schemas.file_model import (
    ContractTypeModel,
    FileTypeModel,
    FileType,
)
from schemas.objects import (
    Event,
    Person,
)
from pydantic_ai import Agent
from datetime import datetime
from tantar.utils.logger import get_logger

logger = get_logger(__name__)


class Context(BaseModel):
    steps: Dict[str, Any]
    previous_step: Optional[str] = None
    current_step: Optional[str] = None


class State(BaseModel):
    name: str
    lambda_func: Optional[Callable] = None
    routing_rules: List[Tuple[Callable, Self]] = Field(default_factory=list)

    async def run(self, context: Context):
        raise NotImplementedError("Subclasses must implement this method")

    def add_rule(self, routing_func: Callable, state: Self) -> None:
        self.routing_rules.append((routing_func, state))


class AgentState(State):
    name: str
    agent: Any
    templating_func: Callable

    async def run(self, context):
        logger.info("LLM agent state start name=%s", self.name)
        context.current_step = self.name

        prompt, message_history = self.templating_func(context)
        logger.info(
            "LLM agent call name=%s prompt_len=%s history_len=%s",
            self.name,
            len(str(prompt)),
            len(message_history) if message_history else 0,
        )
        llm_result = await self.agent.run(prompt, message_history=message_history)
        data = llm_result.data
        logger.info("LLM agent done name=%s", self.name)
        context.steps[self.name] = data
        if self.lambda_func:
            self.lambda_func(context)

        context.previous_step = self.name
        for routing_func, state in self.routing_rules:
            if routing_func(data):
                await state.run(context)


class Demultiplexor(State):
    context_selector: Callable

    async def run(self, context: Context):
        data = self.context_selector(context)
        tasks = []
        for i, datum in enumerate(data):
            step_key = f"{self.name}_{i}"
            context.steps[step_key] = datum
            for routing_func, state in self.routing_rules:
                if routing_func(datum):
                    tasks.append(asyncio.create_task(state.run(context)))
        if tasks:
            await asyncio.gather(*tasks)


class Multiplexor(State):
    pass


file_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=FileTypeModel,
)

event_parser_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Event],
)

contract_classifier_agent = Agent(
    "openai:gpt-4o",
    result_type=ContractTypeModel,
)

persons_agent = Agent(
    "openai:gpt-4o",
    result_type=List[Person],
)


def generate_history(pages: List[str]) -> List[ModelRequest]:
    return [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="You are an expert in legal documents.",
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


def classify_files_template(context: Context):
    pages = context.steps.get("raw_document", [])
    return "Classify this document", generate_history(pages[:2])


def extract_event_template(context: Context):
    pages = context.steps.get("raw_document", [])
    history = generate_history(pages)
    return "Extract the event from this document", history


def classify_contract_template(context: Context):
    pages = context.steps.get("raw_document", [])
    history = generate_history(pages[:2])
    return "Classify This document", history


def extract_persons_from_event_template(context: Context):
    events = context.steps.get("event_parser", [])
    history = generate_history([event.text for event in events])
    return "Extract the persons from this document", history


event_parser_state = AgentState(
    name="event_parser",
    agent=event_parser_agent,
    templating_func=extract_event_template,
)

file_classifier_state = AgentState(
    name="file_classifier",
    agent=file_classifier_agent,
    templating_func=classify_files_template,
)

contract_classifier_state = AgentState(
    name="contract_classifier",
    agent=contract_classifier_agent,
    templating_func=classify_contract_template,
)

# Use the demultiplexor to split the event parser output into separate parallel branches.
event_demultiplexor_state = Demultiplexor(
    name="demultiplexor",
    context_selector=lambda context: context.steps.get("event_parser", []),
)

persons_state = AgentState(
    name="persons_classifier",
    agent=persons_agent,
    templating_func=extract_persons_from_event_template,
)


# Routing rules
def is_process_verbal(data: Any) -> bool:
    return data.type == FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE


def is_contract(data: Any) -> bool:
    return data.type == FileType.CONTRAT


def is_registre_de_mouvement_de_titres(data: Any) -> bool:
    return data.type == FileType.REGISTRE_DE_MOUVEMENT_DE_TITRES


file_classifier_state.add_rule(is_process_verbal, event_parser_state)
file_classifier_state.add_rule(is_contract, contract_classifier_state)
event_parser_state.add_rule(lambda _: True, event_demultiplexor_state)
# In the demultiplexor, the routing rule now receives each datum from the event parser output.
event_demultiplexor_state.add_rule(lambda datum: True, persons_state)
