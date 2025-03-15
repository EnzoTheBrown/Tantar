from tantar.model.classifier import (
    classify_file,
    classify_contract,
    classify_juridic_event,
)
from schemas.model import File, Event, ClassifiedJuridicEvent, EventInput, FileMetadata
from schemas.file_model import FileType, ContractType, EventType
from sqlmodel import select
from tantar.utils.logger import get_logger
from tantar.utils import state
from tantar.pdf_to_image import pdf2images
from tantar.settings import SETTINGS
from tantar.model.ocr import get_blocks, get_page_plane_text
from tantar.model.parser import extract_events, extract_document_metadata
from tantar.vector_database import post_event
import uuid

from typing import List

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
    file: File, text_pages: List[str], file_metadata: FileMetadata
):
    await classify_contract(text_pages)


async def handle_event(file: File, event: Event, file_metadata: FileMetadata):
    event_input = EventInput(
        original_id=str(uuid.uuid4()),
        account_id=file.account.original_id,
        company_id=file.company.original_id,
        file_id=file.original_id,
        date=file_metadata.date.strftime("%Y-%m-%d"),
        text=event.text,
        title=event.title,
        label=event.label,
        type=event.type,
        page_index=event.page_number,
        file_name=file.name,
        siren=file.account.siren,
    )
    post_event(event_input)


async def handle_pv_ag(file: File, text_pages: List[str], file_metadata: FileMetadata):
    events = await extract_events(text_pages)
    for event in events:
        await handle_event(file, event, file_metadata)


async def process_file(db, file: File):
    set_file_status(db, file, state.PROCESSING)
    key = file.s3_path
    images = pdf2images(key, company_id="images")

    image_bytes = [
        s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
        for image in images
    ]
    text_blocks = [get_blocks(image_byte) for image_byte in image_bytes]
    text_pages = [get_page_plane_text(blocks) for blocks in text_blocks]

    file_metadata = await extract_document_metadata(text_pages)

    match file_metadata.type:
        case FileType.CONTRACT:
            await handle_contract(file, text_pages, file_metadata)
        case FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
            await handle_pv_ag(file, text_pages, file_metadata)
        case _:
            raise ValueError(f"Unsupported file type {file_metadata.type}")
