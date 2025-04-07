from tantar.model.classifier import (
    classify_file,
    classify_contract,
    classify_juridic_event,
)
from schemas.model import (
    Company,
    File,
    Event,
    ClassifiedJuridicEvent,
    EventInput,
    FileMetadata,
    ContractChunkInput,
    EventDBModel,
    ContractDBModel,
    EdgeLabel,
    NodeType,
    Account,
    MoralPerson,
    PhysicalPerson,
)
from tantar.graph import create_node, create_edge
from schemas.file_model import FileType, ContractType, EventType
from sqlmodel import select
from tantar.utils.logger import get_logger
from tantar.utils import state
from tantar.pdf_to_image import pdf2images
from tantar.settings import SETTINGS
from tantar.model.ocr import get_blocks, get_page_plane_text
from tantar.model.parser import extract_events, extract_document_metadata
from tantar.vector_database import (
    post_event,
    post_contract_chunk,
    get_contract_chunks_in_vector_db,
)
from tantar.model.tokenizer import tokenize_paragraphs
from tantar.rules.event_to_contract_rules import find_matching_contract_chunks
from tantar.pappers import create_company_details

import uuid

from typing import List, Any

s3 = SETTINGS.s3.client

logger = get_logger(__name__)


def get_unprocessed_files(db):
    return db.exec(select(File).where(File.status == 0)).all()


def set_file_status(db, file, status):
    logger.info(f"setting file status to {status}", extra={"file_id": file.id})
    file.status = status
    db.commit()
    db.refresh(file)


async def handle_contract(
    db, file: File, text_pages: List[str], text_blocks: Any, file_metadata: FileMetadata
):
    contract_type = await classify_contract(text_pages)
    contract_db = ContractDBModel(
        title=file_metadata.title,
        type=contract_type,
        file=file,
    )
    db.add(contract_db)
    db.commit()
    paragraphs = tokenize_paragraphs(text_blocks)
    for paragraph in paragraphs:
        contract_chunk = ContractChunkInput(
            original_id=str(uuid.uuid4()),
            account_id=file.account.original_id,
            company_id=file.company.original_id,
            file_id=file.original_id,
            date=file_metadata.date.strftime("%Y-%m-%d")
            if file_metadata.date
            else None,
            text=paragraph.text,
            title=file_metadata.title,
            page_index=paragraph.page_index,
            file_name=file.name,
            siren=file.company.siren,
            type=contract_type,
        )
        logger.info(f"posting contract chunk {contract_chunk}")
        post_contract_chunk(contract_chunk)


async def handle_event(
    db, file: File, event: Event, file_metadata: FileMetadata
) -> EventInput:
    event_db = EventDBModel(
        text=event.text,
        title=event.title,
        page_index=event.page_index,
        type=event.type,
        label=event.label,
        file=file,
        date=file_metadata.date,
    )
    db.add(event_db)
    db.commit()
    event_input = EventInput(
        original_id=event_db.original_id,
        account_id=file.account.original_id,
        company_id=file.company.original_id,
        file_id=file.original_id,
        date=file_metadata.date.strftime("%Y-%m-%d"),
        text=event.text,
        title=event.title,
        label=event.label,
        type=event.type,
        page_index=event.page_index,
        file_name=file.name,
        siren=file.company.siren,
    )
    logger.info(f"posting event {event_input}")
    post_event(event_input)
    create_node(db, event_input, NodeType.EVENT)
    create_edge(db, file, event_input, EdgeLabel.DECIDES)
    return event_input


async def handle_pv_ag(
    db, file: File, text_pages: List[str], file_metadata: FileMetadata
):
    events = await extract_events(text_pages)
    for event in events:
        event_input = await handle_event(db, file, event, file_metadata)
        for moral_person in event.moral_persons:
            mp_db = db.exec(
                select(MoralPerson).where(
                    MoralPerson.name == moral_person.name,
                )
            ).first()
            if mp_db is None:
                logger.info(f"Creating moral person {moral_person.name}")
                mp_db = MoralPerson(
                    name=moral_person.name,
                )
                db.add(mp_db)
                db.commit()
                db.refresh(mp_db)
                create_node(db, mp_db, NodeType.MORAL_PERSON)
                create_edge(db, event_input, mp_db, EdgeLabel.IS_MENTIONED)
        for physical_person in event.physical_persons:
            pp_db = db.exec(
                select(PhysicalPerson).where(
                    PhysicalPerson.firstname == physical_person.firstname,
                    PhysicalPerson.lastname == physical_person.lastname,
                )
            ).first()
            if pp_db is None:
                logger.info(f"Creating physical person {physical_person.name}")
                pp_db = PhysicalPerson(
                    firstname=physical_person.firstname,
                    lastname=physical_person.lastname,
                )
                db.add(pp_db)
                db.commit()
                db.refresh(pp_db)
                create_node(db, pp_db, NodeType.PHYSICAL_PERSON)
                create_edge(db, event_input, pp_db, EdgeLabel.IS_MENTIONED)


async def run_process_file(original_id: str, account_id: str):
    from tantar.database import get_db

    db = get_db()
    session = next(db)
    file = session.exec(select(File).where(File.original_id == original_id)).first()
    await process_file(session, file, account_id)
    session.close()


async def process_file(db, file: File, account_id: str):
    set_file_status(db, file, state.PROCESSING)
    images = get_images_from_file(file)
    await process_images(db, file, images, account_id)
    set_file_status(db, file, state.PROCESSED)


def get_images_from_file(file: File):
    key = file.s3_path
    return pdf2images(key, company_id="images")


async def get_or_create_company(db, file_metadata: FileMetadata, account_id: str):
    logger.info(f"Getting or creating company {file_metadata.siren}")
    siren = file_metadata.siren
    if siren is None:
        raise ValueError("SIREN not found")

    account = db.exec(select(Account).where(Account.original_id == account_id)).first()
    company = db.exec(
        select(Company).where(
            Company.siren == siren,
            Company.account == account,
        )
    ).first()
    if company is None:
        logger.info(f"The company {siren} does not exist, creating it")
        company = Company(
            siren=siren,
            name=file_metadata.name,
            account=account,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info(f"Creating company details for company {company.original_id}")
        company_details = create_company_details(company)
        db.add(company_details)
        db.commit()
        create_node(db, company, NodeType.COMPANY)
    else:
        logger.info(f"Company {company} already exists")
    return company


async def process_images(db, file: File, images: Any, account_id: str):
    image_bytes = [
        s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
        for image in images
    ]
    text_blocks = [get_blocks(image_byte) for image_byte in image_bytes]
    text_pages = [get_page_plane_text(blocks) for blocks in text_blocks]

    file_metadata = await extract_document_metadata(text_pages)
    company = await get_or_create_company(db, file_metadata, account_id)
    file.company = company
    file.type = file_metadata.type
    db.commit()
    db.refresh(file)

    match file_metadata.type:
        case FileType.CONTRAT:
            create_node(db, file, NodeType.CONTRACT)
            await handle_contract(db, file, text_pages, text_blocks, file_metadata)
        case FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
            create_node(db, file, NodeType.PV_AG)
            create_edge(db, company, file, EdgeLabel.ORGANIZED)
            await handle_pv_ag(db, file, text_pages, file_metadata)
        case _:
            raise ValueError(f"Unsupported file type {file_metadata.type}")


async def update_links(db):
    events = db.exec(select(EventDBModel)).all()
    for event in events:
        contract_chunks = await find_matching_contract_chunks(event)
        if not contract_chunks:
            logger.info("No contract found for this event")
            continue
        contract_chunk = contract_chunks[0]
        file = db.exec(
            select(File).where(File.original_id == contract_chunk.file_id)
        ).first()
        logger.info(
            "Finding a link between an event and a contract",
            extra={
                "file_id": file.id,
                "event_id": event.original_id,
                "contract_chunk_id": contract_chunk.original_id,
            },
        )
        create_edge(
            db,
            source=event,
            target=file,
            label=EdgeLabel.AUTHORIZED,
        )
