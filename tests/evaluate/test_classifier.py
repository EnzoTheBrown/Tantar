from tantar.model.classifier import (
    classify_file,
    classify_contract,
    classify_juridic_event,
)
import pytest
from pdf2image import convert_from_path
from schemas.file_model import FileType, JuridicCategory, EventType, ContractType
from tantar.model.ocr import get_blocks, get_page_plane_text
import io


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
async def test_classfy_file(pages):
    file_type = await classify_file(pages)
    assert file_type == FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE
