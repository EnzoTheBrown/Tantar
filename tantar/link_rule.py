from schemas.model import (
    VectorEvent,
    File,
    ContractType,
    EventType,
)
from sqlmodel import select
from tantar.graph import create_edge
from tantar.vector_database import (
    get_contract_chunks_in_vector_db,
)
from datetime import datetime, timedelta
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

MAX_TIME_DELTA_WEEKS = 3 * 4


def convert_date_string_to_datetime(date_string: str):
    return datetime.strptime(date_string, "%Y-%m-%d")


def convert_datetime_to_date_string(date: datetime):
    return date.strftime("%Y-%m-%d")


def link_contract_authorization_event_transfert_de_siege_social(db, event: VectorEvent):
    assert event.type == EventType.TRANSFERT_DE_SIEGE_SOCIAL, (
        'Event must be of type "TRANSFERT_DE_SIEGE_SOCIAL"'
    )
    date = convert_date_string_to_datetime(event.date)
    start_date = date - timedelta(weeks=MAX_TIME_DELTA_WEEKS)
    end_date = date + timedelta(weeks=MAX_TIME_DELTA_WEEKS)

    contract_chunks = get_contract_chunks_in_vector_db(
        question=event.text,
        metadata=f"account_id='{event.account_id}' AND date<='{end_date}' AND date>='{start_date}' AND siren='{event.siren}' AND type='{ContractType.BAIL.value}'",
        limit=1,
    )

    if not contract_chunks:
        logger.info("No contract found for this decision")
        return None

    contract_chunk = contract_chunks[0]

    file = db.exec(
        select(File).where(File.original_id == contract_chunk.file_id)
    ).first()

    logger.info(
        "Finding a link between an event and a contract of type BAIL",
        extra={
            "file_id": file.id,
            "event_id": event.original_id,
            "contract_chunk_id": contract_chunk.original_id,
        },
    )
    create_edge(
        db,
        source=file,
        target=event,
        label="HAS_AUTHORIZED",
    )


def link_contract_authorization_event_demande_pret_bancaire(db, event: VectorEvent):
    assert event.type == EventType.DEMANDE_DE_PRET_BANCAIRE, (
        'Event must be of type "DEMANDE_DE_PRET_BANCAIRE"'
    )
    date = convert_date_string_to_datetime(event.date)
    start_date = date - timedelta(weeks=MAX_TIME_DELTA_WEEKS)
    end_date = date + timedelta(weeks=MAX_TIME_DELTA_WEEKS)

    contract_chunks = get_contract_chunks_in_vector_db(
        question=event.text,
        metadata=f"account_id='{event.account_id}' AND date<='{end_date}' AND date>='{start_date}' AND siren='{event.siren}' AND type='{ContractType.PRET_BANCAIRE.value}'",
        limit=1,
    )

    if not contract_chunks:
        logger.info("No contract found for this decision")
        return None

    contract_chunk = contract_chunks[0]

    file = db.exec(
        select(File).where(File.original_id == contract_chunk.file_id)
    ).first()

    logger.info(
        "Finding a link between an event and a contract of type DEMANDE_DE_PRET_BANCAIRE",
        extra={
            "file_id": file.id,
            "event_id": event.original_id,
            "contract_chunk_id": contract_chunk.original_id,
        },
    )
    create_edge(
        db,
        target=file,
        source=event,
        label="HAS_AUTHORIZED",
    )
