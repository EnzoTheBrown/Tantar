from tantar.utils.logger import get_logger

logger = get_logger(__name__)


def create_node(db, entity, type):
    logger.info("Skipping graph node creation (minimal relational DB).")
    return None


def get_node(db, original_id: str):
    logger.info("Skipping graph node lookup (minimal relational DB).")
    return None


def create_edge(db, source, target, label: str):
    logger.info("Skipping graph edge creation (minimal relational DB).")
    return None


def get_nodes(db):
    return []


def get_neighbors(db, source_id: str, label: str | None = None):
    return []
