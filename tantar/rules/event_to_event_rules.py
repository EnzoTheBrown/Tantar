from schemas.model import EventDBModel, EventType, ContractChunk
from tantar.vector_database import get_events_in_vector_db, VectorEvent
from typing import List, Optional
from datetime import timedelta


def within_the_same_year(event: EventDBModel) -> str:
    pass


async def find_matching_events(
    event: EventDBModel,
) -> Optional[List[VectorEvent]]:
    match event.type:
        case EventType.DECISION_DE_DISTRIBUTION_DE_DIVIDENDES:
            return get_events_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{event.account_id}'
                    AND siren='{event.siren}'
                    AND type='{EventType.DECISION_D_APPROBATION_DES_COMPTES_ANNUELS.value}'
                    AND {within_the_same_year(event)}
                """,
            )
