from tantar.utils.logger import get_logger

logger = get_logger(__name__)


def run_graph(*_args, **_kwargs):
    logger.info("AI graph pipeline disabled (minimal relational DB).")
    return None
