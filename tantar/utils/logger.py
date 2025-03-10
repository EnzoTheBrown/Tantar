import logging
import json
import logfire


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logs."""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        return json.dumps(log_record)


def configure_logfire():
    """Configure Logfire for log monitoring."""
    logfire.configure()


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Set up a JSON logger with Logfire integration."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = JsonFormatter()
    logfire_handler = logfire.LogfireLoggingHandler()
    logfire_handler.setFormatter(formatter)
    if not any(isinstance(h, logfire.LogfireLoggingHandler) for h in logger.handlers):
        logger.addHandler(logfire_handler)

    return logger


configure_logfire()

