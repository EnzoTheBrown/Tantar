from typing import Optional, List
from schemas.vector import EventVector


def within_the_same_year(event: EventVector) -> str:
    return "1 = 1"


def find_matching_event(event: EventVector) -> Optional[List[EventVector]]:
    return None
