from tantar.utils.logger import get_logger
from tantar.utils import state
from schemas.relational import File
from tantar.database import get_db
from sqlmodel import select
from time import sleep
import asyncio

logger = get_logger(__name__)


def get_unprocessed_files(db):
    return db.exec(select(File).where(File.status == 0)).all()


def set_file_status(db, file, status):
    logger.info("setting file status to %s", status, extra={"file_id": file.id})
    file.status = status
    db.commit()
    db.refresh(file)


def run():
    from process_file import process_file

    logger.info("Starting worker")
    db = next(get_db())
    files = get_unprocessed_files(db)
    logger.info("Found %s unprocessed files", len(files))
    loop = asyncio.get_event_loop()
    for file in files:
        loop.run_until_complete(process_file(db, file))
    db.close()


def main():
    while True:
        run()
        sleep(5)


if __name__ == "__main__":
    main()
