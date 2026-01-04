from sqlmodel import select
from schemas.relational import File
from tantar.utils.logger import get_logger
from tantar.utils import state
from tantar.process_file import process_file as core_process_file

logger = get_logger(__name__)


def get_unprocessed_files(db):
    return db.exec(select(File).where(File.status == 0)).all()


def set_file_status(db, file, status):
    logger.info("setting file status to %s", status, extra={"file_id": file.id})
    file.status = status
    db.commit()
    db.refresh(file)


async def process_file(db, file: File, account_id: str | None = None):
    set_file_status(db, file, state.PROCESSING)
    await core_process_file(db, file)
    set_file_status(db, file, state.PROCESSED)


async def update_links(db):
    logger.info("Skipping update_links (events-only vector DB).")
