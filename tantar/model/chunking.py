from typing import List, Iterator, Optional
MAX_TOKEN = 5000


def page_overlapping(pages: List[str], overlap: float = 0.1) -> Iterator[str]:
    """
    Considering the number max of tokens (words/characters),
    return either an overlapping of the previous and next pages or a single page with all the information.
    Args:
        pages (List[str]): A list of page content as strings.
        overlap (float): A percentage (0 < overlap < 1) of how much content to include from the previous and next pages.

    Yields:
        str: A string representing the combined content of the current page with its context.
    """
    if not (0 < overlap < 1):
        raise ValueError("Overlap must be a float between 0 and 1.")
    if len(' '.join(pages).split(' ')) < MAX_TOKEN:
        yield ' '.join(pages)
    else:
        padded: List[Optional[str]] = [None] + pages + [None]
        for previous_page, page, next_page in zip(padded[:-2], padded[1:-1], padded[2:]):
            overlap_previous = (
                previous_page[-int(len(previous_page) * overlap):] if previous_page else ""
            )
            overlap_next = (
                next_page[:int(len(next_page) * overlap)] if next_page else ""
            )
            yield f"{overlap_previous}\n{page}\n{overlap_next}"
