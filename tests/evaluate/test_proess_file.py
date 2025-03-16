import pytest
from schemas.model import File
from process_file import process_file


@pytest.mark.asyncio
async def test_process_file(db, file: File):
    await process_file(db, file)
    db.refresh(file)
    assert file.status == 2
