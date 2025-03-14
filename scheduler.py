import traceback
from tantar.pappers import create_company_details
from tantar.utils.logger import get_logger
from tantar.graph import create_node, create_edge
from tantar.utils import state
from tantar.model import model
from tantar.settings import SETTINGS
from tantar.pdf_to_image import pdf2images
from tantar.vector_database import (
    post_contract_chunk,
    post_event,
    EventInput,
    ContractChunkInput,
)
from tantar.model.classifier import FileType
from schemas.model import Company, File
from tantar.database import get_db
from sqlmodel import select
from time import sleep
import requests
import uuid
import asyncio
from datetime import datetime

s3 = SETTINGS.s3.client

logger = get_logger(__name__)


def get_unprocessed_files(db):
    return db.exec(select(File).where(File.status == 0)).all()


def set_file_status(db, file, status):
    logger.info(f"setting file status to {status}", extra={"file_id": file.id})
    file.status = status
    db.commit()
    db.refresh(file)


def run():
    logger.info("Starting worker")
    db = next(get_db())
    files = get_unprocessed_files(db)
    logger.info(f"Found {len(files)} unprocessed files")
    loop = asyncio.get_event_loop()
    for file in files:
        loop.run_until_complete(process_file(db, file))
    db.close()


def create_event(event, metadata, file, token):
    logger.info(
        "AUDIT: creating event",
        extra={"file_id": file.id, "page_number": event.page_number, "audit": True},
    )
    event_dict = {
        "date": metadata.date.strftime("%Y-%m-%d"),
        "text": event.text,
        "title": event.title,
        "label": event.label.name,
        "page_index": event.page_number,
        "file_id": file.original_id,
    }
    response = requests.post(
        f"{SETTINGS.app.url}/company/{file.company.original_id}/event",
        json=event_dict,
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 201:
        logger.info("Event added")
    else:
        logger.error(f"Event Not added {response.status_code} {response.content}")


def create_company(db, account, metadata):
    logger.info("AUDIT: creating company", extra={"audit": True})
    company = Company(
        name=metadata.name,
        siren=metadata.siren,
        account=account,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    try:
        company_details = create_company_details(company)
        db.add(company_details)
        db.commit()
    except Exception as e:
        logger.error(f"Error while creating company details: {e}")
    return company


def move_file(db, file, company):
    logger.info("AUDIT: Moving file to company", extra={"audit": True})
    file.company_id = company.id
    db.commit()
    db.refresh(file)
    s3_key = f"{company.account.original_id}/{company.original_id}/{file.original_id}"
    s3.copy_object(
        Bucket=SETTINGS.s3.bucket,
        CopySource=f"{SETTINGS.s3.bucket}/{file.s3_path}",
        Key=s3_key,
    )
    s3.delete_object(Bucket=SETTINGS.s3.bucket, Key=file.s3_path)
    file.s3_path = s3_key
    db.commit()
    db.refresh(file)


async def process_file(db, file):
    logger.info("AUDIT: Processing file", extra={"file_id": file.id, "audit": True})
    try:
        set_file_status(db, file, state.PROCESSING)
        key = file.s3_path
        images = pdf2images(key, company_id="images")
        image_bytes = [
            s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
            for image in images
        ]
        document = await model(image_bytes)
        file.type = document.metadata.type
        db.commit()
        db.refresh(file)
        siren = document.metadata.siren
        if siren is None:
            logger.error("SIREN not found")
            set_file_status(db, file, state.ERROR)
            return
        if file.company is None:
            company = (
                db.query(Company)
                .filter(Company.siren == siren, Company.account_id == file.account_id)
                .first()
            )
            if company is None:
                assert file.account is not None, "Account is required"
                logger.info(
                    f"AUDIT: Creating company for account {file.account.original_id}"
                )
                company = create_company(db, file.account, document.metadata)
                create_node(db, company)
            if company is None:
                set_file_status(db, file, state.ERROR)
                return
            move_file(db, file, company)
        if file.company.siren != siren:
            logger.error("SIREN mismatch")
            set_file_status(db, file, state.ERROR)
            return
        if not document.file_chunks:
            logger.info("AUDIT: No event to create")
            return

        if document.metadata.type == FileType.PVAG:
            create_edge(db, file.company, file, "HAS_ORGANIZED")
            for event in document.file_chunks:
                logger.info(
                    f"Adding new event {event.title}: {event.title} for {file.company.original_id}"
                )
                event_input = EventInput(
                    original_id=str(uuid.uuid4()),
                    account_id=file.account.original_id,
                    company_id=file.company.original_id,
                    file_id=file.original_id,
                    date=document.metadata.date.strftime("%Y-%m-%d"),
                    text=event.text,
                    title=event.title,
                    label=event.label,
                    type=event.type,
                    page_index=event.page_number,
                    file_name=file.name,
                    siren=siren,
                )
                create_node(db, event_input)
                create_edge(db, file, event_input, "HAS_DECIDED")
                post_event(event_input)
            set_file_status(db, file, state.PROCESSED)
        elif document.metadata.type == FileType.CONTRACT:
            create_edge(db, file.company, file, FileType.CONTRACT)
            contract = document.additional_data
            logger.info(f"Adding new contract {contract}")
            db.add(contract.offeror)
            db.commit()
            db.add(contract.offeree)
            db.commit()
            create_node(db, contract.offeror)
            create_node(db, contract.offeree)
            create_edge(db, file, contract.offeror, "HAS_OFFEROR")
            create_edge(db, file, contract.offeree, "HAS_OFFEREE")
            if contract is None:
                raise ValueError("Contract not found")
            for chunk in document.file_chunks:
                logger.info("Adding new contract chunk")
                contract_chunk = ContractChunkInput(
                    original_id=str(uuid.uuid4()),
                    account_id=file.account.original_id,
                    text=chunk.text,
                    type=contract.type,
                    page_index=chunk.page_number,
                    file_id=file.original_id,
                    file_name=file.name,
                    date=document.metadata.date.strftime("%Y-%m-%d")
                    if document.metadata.date
                    else datetime.now().strftime("%Y-%m-%d"),
                    company_id=file.company.original_id,
                    siren=siren,
                )
                post_contract_chunk(contract_chunk)
            set_file_status(db, file, state.PROCESSED)
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))
        set_file_status(db, file, state.ERROR)


def main():
    while True:
        run()
        sleep(5)


if __name__ == "__main__":
    main()
