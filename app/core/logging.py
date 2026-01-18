"""
Logging Configuration

Sets up structured logging for the application.
"""

import logging
import sys
from typing import Literal

from app.config import settings


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Optional override for log level. Defaults based on ENV.
    """
    # Determine log level
    if level:
        log_level = getattr(logging, level)
    elif settings.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # App logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)

    logging.info(f"Logging configured: level={logging.getLevelName(log_level)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Configured logger instance
    
    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)
