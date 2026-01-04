from tantar.settings import SETTINGS
from tantar.pdf_to_image import pdf2images
from tantar.model.ocr import get_blocks, get_page_plane_text
from typing import List
from tantar.model.classifier import classify_file
from tantar.model.parser import extract_events, extract_document_metadata
from schemas.file_model import FileType
from schemas.relational import File, User
from schemas.vector import EventInput
from tantar.vector_database import post_event
from sqlmodel import select, Session
from uuid import uuid4
from tantar.controller import get_or_create_company
from tantar.pappers import create_company_details
from tantar.utils.logger import get_logger
from tantar.database import engine

logger = get_logger(__name__)

s3 = SETTINGS.s3.client


async def pdf_to_images(pdf_path: str) -> List[bytes]:
    images = pdf2images(pdf_path, company_id="images")
    images_bytes = [
        s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
        for image in images
    ]

    return images_bytes


async def ocr(file_bytes: list[bytes]):
    return [get_blocks(image_byte) for image_byte in file_bytes]


async def get_pages(text_blocks):
    return [get_page_plane_text(blocks) for blocks in text_blocks]


async def process_file(
    db: Session,
    file: File,
) -> File:
    file_id = getattr(file, "original_id", None) or getattr(file, "id", None)
    logger.info("process_file start file_id=%s name=%s", file_id, file.name)
    file_bytes = await pdf_to_images(file.s3_path)
    if not file_bytes:
        logger.error("No images returned from OCR pipeline", extra={"file_id": file.id})
        return file
    logger.info(
        "process_file pdf_to_images done file_id=%s page_count=%s",
        file_id,
        len(file_bytes),
    )
    text_blocks = await ocr(file_bytes)
    logger.info("process_file ocr done file_id=%s", file_id)
    pages = await get_pages(text_blocks)
    logger.info(
        "process_file get_pages done file_id=%s page_count=%s",
        file_id,
        len(pages),
    )
    file_type = await classify_file(pages)
    logger.info("process_file classify_file done file_id=%s type=%s", file_id, file_type)
    file.type = file_type
    db.add(file)
    db.commit()
    db.refresh(file)

    file_metadata = await extract_document_metadata(pages)
    logger.info(
        "process_file extract_document_metadata done file_id=%s name=%s siren=%s",
        file_id,
        file_metadata.name,
        file_metadata.siren,
    )
    create, company = await get_or_create_company(
        db=db,
        name=file_metadata.name,
        siren=file_metadata.siren,
        user_id=file.user_id,
    )
    if create:
        create_company_details(company, db=db)
        db.commit()
        db.refresh(company)
    file.company = company
    db.add(file)
    db.commit()
    db.refresh(file)

    if file.type == FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
        events = await extract_events(pages)
        user = db.exec(select(User).where(User.id == file.user_id)).first()
        account_id = user.original_id if user else ""
        for event in events:
            event_input = EventInput(
                original_id=str(uuid4()),
                account_id=account_id,
                company_id=file.company.original_id,
                file_id=file.original_id,
                date=file_metadata.date.strftime("%Y-%m-%d")
                if file_metadata.date
                else "",
                text=event.text,
                title=event.title,
                label=event.label,
                type=event.type,
                page_index=event.page_index,
                file_name=file.name,
                siren=file.company.siren,
            )
            post_event(event_input)

    logger.info("process_file done file_id=%s type=%s", file_id, file.type)
    return file


async def run_process_file(file_original_id: str) -> None:
    with Session(engine) as db:
        file = db.exec(select(File).where(File.original_id == file_original_id)).first()
        if file is None:
            logger.error(
                "process_file missing file",
                extra={"file_original_id": file_original_id},
            )
            return
        await process_file(db=db, file=file)
