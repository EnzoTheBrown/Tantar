from typing import Optional
from schemas.vector import EventVector
from tantar.utils.logger import get_logger

logger = get_logger(__name__)


def link_contract_authorization_event_transfert_de_siege_social(db, event: EventVector):
    logger.info("Skipping link rule (events-only vector DB).")
    return None


def link_contract_authorization_event_demande_pret_bancaire(db, event: EventVector):
    logger.info("Skipping link rule (events-only vector DB).")
    return None
