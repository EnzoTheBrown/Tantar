import pytest
from schemas.model import File
from process_file import process_file, update_links
from tantar.utils import state


@pytest.mark.asyncio
async def test_process_file_pv_ag(db, pv_ag: File):
    assert pv_ag.status == state.PENDING
    await process_file(db, pv_ag)
    db.refresh(pv_ag)
    assert pv_ag.status == state.PROCESSED


@pytest.mark.asyncio
async def test_process_file_contract(db, contract: File):
    assert contract.status == state.PENDING
    await process_file(db, contract)
    db.refresh(contract)
    assert contract.status == state.PROCESSED
    await update_links(db)
