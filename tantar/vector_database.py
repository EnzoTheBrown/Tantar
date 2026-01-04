import lancedb
from typing import List, Optional
from schemas.vector import (
    EventVector,
    EventInput,
    JuridicCategory,
    ContractChunk,
    ContractChunkInput,
    MoralPersonInput,
    PhysicalPersonInput,
)
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

lance_db = lancedb.connect("db/database.lance")

try:
    events_table = lance_db.open_table("events")
except Exception:
    events_table = lance_db.create_table("events", schema=EventVector)


def insert_events_in_vector_db(events: List[EventInput]):
    events_table.add(events)


def get_events_in_vector_db(
    question: Optional[str] = None, metadata: Optional[str] = None, limit: int = 10
) -> List[EventVector]:
    try:
        if question is None:
            search_query = events_table.search()
        else:
            search_query = events_table.search(question)
        if metadata is not None:
            search_query = search_query.where(metadata)
        return search_query.limit(limit).to_pydantic(EventVector)
    except Exception as exc:
        logger.error(f"Error querying events in vector DB: {exc}")
        if "Not found" in str(exc):
            logger.warning("Recreating events vector table due to missing lance data")
            recreate_events_table()
        return []


def recreate_events_table() -> None:
    global events_table
    try:
        if "events" in lance_db.table_names():
            lance_db.drop_table("events")
    except Exception as exc:
        logger.error(f"Failed to drop events table: {exc}")
    events_table = lance_db.create_table("events", schema=EventVector)


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


# ---------------------------------------------------------------------------
# Deprecated stubs (events-only vector DB)
# ---------------------------------------------------------------------------


def post_contract_chunk(contract_chunk: ContractChunkInput):
    logger.info("Skipping contract chunk insert (events-only vector DB).")


def get_contract_chunks_in_vector_db(
    question: Optional[str] = None, metadata: Optional[str] = None, limit: int = 10
) -> List[ContractChunk]:
    logger.info("Skipping contract chunk query (events-only vector DB).")
    return []


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
    return []


def insert_moral_person(person: MoralPersonInput):
    logger.info("Skipping moral person insert (events-only vector DB).")


def insert_physical_person(person: PhysicalPersonInput):
    logger.info("Skipping physical person insert (events-only vector DB).")


def get_moral_persons(
    question: Optional[str] = None,
    metadata: Optional[str] = None,
    limit: int = 10,
) -> List[MoralPersonInput]:
    logger.info("Skipping moral person query (events-only vector DB).")
    return []


def get_physical_persons(
    question: Optional[str] = None,
    metadata: Optional[str] = None,
    limit: int = 10,
) -> List[PhysicalPersonInput]:
    logger.info("Skipping physical person query (events-only vector DB).")
    return []
