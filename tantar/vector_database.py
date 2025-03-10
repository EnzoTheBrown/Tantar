import lancedb
from typing import List, Optional
from schemas.model import (
    VectorEvent,
    EventInput,
    ContractChunk,
    ContractChunkInput,
    Event,
    JuridicCategory,
)
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

db = lancedb.connect(
    "s3://tantar/pitantar/database.lance", storage_options={"timeout": "60s"}
)

try:
    contract_chunks_table = db.open_table("contracts")
except Exception as e:
    logger.info("Creating contracts table")
    contract_chunks_table = db.create_table("contracts", schema=ContractChunk)

try:
    events_table = db.open_table("events")
except Exception as e:
    events_table = db.create_table("events", schema=VectorEvent)


def insert_contract_chunks(contract_chunks: List[ContractChunkInput]):
    contract_chunks_table.add(contract_chunks)


def get_contract_chunks_in_vector_db(
    question: Optional[str] = None, metadata: Optional[str] = None, limit: int = 10
) -> List[ContractChunk]:
    if question is None:
        search_query = contract_chunks_table.search()
    else:
        search_query = contract_chunks_table.search(question)
    if metadata is not None:
        search_query = search_query.where(metadata)
    return search_query.limit(limit).to_pydantic(ContractChunk)


def insert_events_in_vector_db(events: List[EventInput]):
    events_table.add(events)


def get_events_in_vector_db(
    question: Optional[str] = None, metadata: Optional[str] = None, limit: int = 10
) -> List[VectorEvent]:
    if question is None:
        search_query = events_table.search()
    else:
        search_query = events_table.search(question)
    if metadata is not None:
        search_query = search_query.where(metadata)
    return search_query.limit(limit).to_pydantic(VectorEvent)


def get_events(
    account_id: str,
    question: Optional[str],
    siren: Optional[str],
    label: Optional[JuridicCategory],
    k: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    company_id: Optional[str] = None,
) -> List[Event]:
    metadata = [f"account_id='{account_id}'"]
    if company_id is not None:
        metadata.append(f"company_id='{company_id}'")
    if label is not None:
        metadata.append(f"label='{label.value}'")
    if start_date is not None:
        metadata.append(f"date>='{start_date}'")
    if end_date is not None:
        metadata.append(f"date<='{end_date}'")
    if siren is not None:
        metadata.append(f"siren='{siren}'")
    metadata = " AND ".join(metadata)
    logger.info(f"Getting events from Pitantar with metadata: {metadata}")
    return get_events_in_vector_db(question, metadata, k)


def post_event(event: EventInput):
    logger.info(f"Inserting event in Pitantar: {event}")
    insert_events_in_vector_db([event.model_dump()])
    return event


def get_contract_chunks(
    account_id: str,
    question: Optional[str],
    siren: Optional[str],
    label: Optional[JuridicCategory],
    k: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    company_id: Optional[str] = None,
) -> List[ContractChunk]:
    metadata = [f"account_id='{account_id}'"]
    if company_id is not None:
        metadata.append(f"company_id='{company_id}'")
    if label is not None:
        metadata.append(f"label='{label.value}'")
    if start_date is not None:
        metadata.append(f"date>='{start_date}'")
    if end_date is not None:
        metadata.append(f"date<='{end_date}'")
    if siren is not None:
        metadata.append(f"siren='{siren}'")
    metadata = " AND ".join(metadata)
    return get_contract_chunks_in_vector_db(question, metadata, k)


def post_contract_chunk(contract_chunk: ContractChunkInput):
    insert_contract_chunks([contract_chunk.model_dump()])
