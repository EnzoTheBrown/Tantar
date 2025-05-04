import lancedb
from typing import List, Optional
from schemas.vector import (
    EventVector,
    EventInput,
    ContractChunk,
    ContractChunkInput,
    JuridicCategory,
    MoralPersonVector,
    PhysicalPersonVector,
    MoralPersonInput,
    PhysicalPersonInput,
)
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

db = lancedb.connect("db/database.lance")

try:
    contract_chunks_table = db.open_table("contracts")
except Exception as e:
    logger.info("Creating contracts table")
    contract_chunks_table = db.create_table("contracts", schema=ContractChunk)

try:
    events_table = db.open_table("events")
except Exception as e:
    events_table = db.create_table("events", schema=EventVector)


try:
    persons_table = db.open_table("moral_persons")
except Exception as e:
    logger.info("Creating persons table")
    persons_table = db.create_table("moral_persons", schema=MoralPersonVector)


try:
    physical_persons_table = db.open_table("physical_persons")
except Exception as e:
    logger.info("Creating physical persons table")
    physical_persons_table = db.create_table(
        "physical_persons", schema=PhysicalPersonVector
    )


def insert_contract_chunks(contract_chunks: List[ContractChunkInput]):
    contract_chunks_table.add(contract_chunks)


def get_contract_chunks_in_vector_db(
    question: Optional[str] = None, metadata: Optional[str] = None, limit: int = 10
) -> List[ContractChunk]:
    logger.info(f"Getting contract chunks from Pitantar with metadata: {metadata}")
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
) -> List[EventVector]:
    if question is None:
        search_query = events_table.search()
    else:
        search_query = events_table.search(question)
    if metadata is not None:
        search_query = search_query.where(metadata)
    return search_query.limit(limit).to_pydantic(EventVector)


def get_events(
    account_id: str,
    question: Optional[str],
    siren: Optional[str],
    label: Optional[JuridicCategory],
    k: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    company_id: Optional[str] = None,
) -> List[EventVector]:
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


def insert_moral_person(person: MoralPersonInput):
    persons_table.add([person])


def get_moral_persons(
    question: Optional[str] = None,
    metadata: Optional[str] = None,
    limit: int = 10,
) -> List[MoralPersonInput]:
    if question is None:
        search_query = persons_table.search()
    else:
        search_query = persons_table.search(question)
    if metadata is not None:
        search_query = search_query.where(metadata)
    return search_query.limit(limit).to_pydantic(MoralPersonInput)


def insert_physical_person(person: PhysicalPersonInput):
    physical_persons_table.add([person])


def get_physical_persons(
    question: Optional[str] = None,
    metadata: Optional[str] = None,
    limit: int = 10,
) -> List[PhysicalPersonInput]:
    if question is None:
        search_query = physical_persons_table.search()
    else:
        search_query = physical_persons_table.search(question)
    if metadata is not None:
        search_query = search_query.where(metadata)
    return search_query.limit(limit).to_pydantic(PhysicalPersonInput)
