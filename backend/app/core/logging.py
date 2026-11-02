"""Application logging configuration with security filters to sanitize sensitive credentials."""
import logging
import re
import sys

# Regex pattern to identify potential API keys or tokens
KEY_PATTERN = re.compile(r"(xai-[a-zA-Z0-9_-]{10,}|sk-[a-zA-Z0-9_-]{10,})")


class RedactingFormatter(logging.Formatter):
    """Log formatter that automatically masks API keys and credentials."""

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        if isinstance(msg, str):
            msg = KEY_PATTERN.sub("[REDACTED_API_KEY]", msg)
        return msg


def setup_logger(name: str = "ari") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = RedactingFormatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger("ari")
