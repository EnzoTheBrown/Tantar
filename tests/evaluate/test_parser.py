from tantar.model.parser import (
    extract_events,
    extract_document_metadata,
)
import pytest
from pdf2image import convert_from_path
from tantar.model.ocr import get_blocks, get_page_plane_text
import io
from schemas.file_model import FileType, JuridicCategory, EventType


def pdf_to_pages(filepath):
    images = convert_from_path(filepath)
    pages = []
    for image in images:
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            image_bytes = output.getvalue()
        blocks = get_blocks(image_bytes)
        text = get_page_plane_text(blocks)
        pages.append(text)
    return pages


files = ["datasets/CLARTE AUTOMOBILES/CLARTE AUTOMOBILES - Actes du 03-11-2016.pdf"]


@pytest.mark.parametrize("pages", [pdf_to_pages(file) for file in files])
@pytest.mark.asyncio
async def test_extract_document_metadata(pages):
    metadata = await extract_document_metadata(pages)

    assert metadata.type == FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE
    assert metadata.siren == "807385026"
    assert metadata.name == "CLARTE AUTOMOBILES"


@pytest.mark.parametrize("pages", [pdf_to_pages(file) for file in files])
@pytest.mark.asyncio
async def test_extract_events(pages):
    events = await extract_events(pages)
    assert events
    assert events[0].type == EventType.TRANSFERT_DE_SIEGE_SOCIAL
    assert events[0].label == JuridicCategory.MODIFICATIONS_STATUTAIRES
