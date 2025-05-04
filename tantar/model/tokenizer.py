from schemas.vector import FileChunk
from typing import Any, List


def tokenize_paragraphs(
    pages_blocks: Any, gap_threshold: float = 0.02
) -> List[FileChunk]:
    """
    Splits an OCR'd document into paragraphs based on vertical spacing.

    Args:
        image_bytes (bytes): The image content.
        gap_threshold (float): The normalized vertical gap (relative to the image height)
                               to decide if a new paragraph has started.
    Returns:
        List[str]: A list of paragraphs.
    """
    paragraphs = []
    for page, blocks in enumerate(pages_blocks):
        line_blocks = [block for block in blocks if block.get("BlockType") == "LINE"]
        line_blocks.sort(key=lambda b: b["Geometry"]["BoundingBox"]["Top"])
        current_paragraph = ""
        previous_bottom = None
        for block in line_blocks:
            bbox = block["Geometry"]["BoundingBox"]
            top = bbox["Top"]
            height = bbox["Height"]
            bottom = top + height
            if previous_bottom is not None:
                if (top - previous_bottom) > gap_threshold:
                    paragraph = FileChunk(
                        text=current_paragraph.strip(), page_index=page
                    )
                    paragraphs.append(paragraph)
                    current_paragraph = ""
            current_paragraph += block["Text"] + " "
            previous_bottom = bottom
        if current_paragraph.strip():
            paragraph = FileChunk(text=current_paragraph.strip(), page_index=page)
            paragraphs.append(paragraph)
    return paragraphs
