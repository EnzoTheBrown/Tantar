from typing import Any
from tantar.settings import SETTINGS
from tantar.utils.logger import get_logger
from .parser import extract_events
from .tokenizer import tokenize_paragraphs
from .classifier import classify_file, FileType, classify_contract
from .ocr import get_blocks, get_page_plane_text
from typing import List, Optional, Any
from schemas.model import Contract, FileChunk, FileMetadata
from pydantic import BaseModel

logger = get_logger(__name__)


class Document(BaseModel):
    file_chunks: Optional[List[FileChunk]] = []
    metadata: Optional[FileMetadata] = None
    additional_data: Optional[Any] = None


async def extract_events_from_pv_ag(
    text_pages: List[str], file_metadata: FileMetadata
) -> Document:
    logger.info("new document to parse")
    events = await extract_events(text_pages)
    return Document(file_chunks=events, metadata=file_metadata)


def extract_paragraphs_from_contract(
    text_blocks: Any, file_metadata: FileMetadata, contract: Contract
) -> Document:
    logger.info("new document to parse")
    paragraphs = tokenize_paragraphs(text_blocks)
    return Document(
        file_chunks=paragraphs,
        metadata=file_metadata,
        additional_data=contract,
    )


async def model(image_bytes: List[bytes]) -> Document:
    logger.info("new document to parse")
    text_blocks = [get_blocks(image_byte) for image_byte in image_bytes]
    text_pages = [get_page_plane_text(blocks) for blocks in text_blocks]

    metadata = await classify_file(text_pages)

    if metadata.type == FileType.PVAG:
        logger.info("extracting events from pv ag")
        return await extract_events_from_pv_ag(text_pages, metadata)
    if metadata.type == FileType.CONTRACT:
        logger.info("extracting paragraphs from contract")
        contract = await classify_contract(text_pages)
        return extract_paragraphs_from_contract(text_blocks, metadata, contract)
    else:
        raise ValueError(f"Unsupported file type {metadata.type}")
