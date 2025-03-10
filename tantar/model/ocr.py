from tantar.settings import SETTINGS
from tantar.utils.logger import get_logger
from typing import Any

textract = SETTINGS.textract.client

logger = get_logger(__name__)


def get_blocks(image_bytes: bytes):
    response = textract.detect_document_text(Document={"Bytes": image_bytes})
    return response["Blocks"]


def get_page_plane_text(blocks: Any) -> str:
    logger.info("calling textract")
    text = ""
    for item in blocks:
        if item["BlockType"] == "LINE":
            text += item["Text"] + "\n"
    return text
