"""
Title: Loguru Logging Configuration

Author: Claude AI

Description:
Centralized logging configuration using loguru with colored output and file
rotation. Provides both console and file logging with appropriate formatting.

Usage:
    from reddit_wsb_stocks.logging_config import setup_logging, get_logger

    setup_logging()
    logger = get_logger(__name__)
    logger.info("application_started", version="1.0.0")

Notes:
    - Logs are rotated daily and kept for 30 days
    - Console output includes colored level names
    - File output uses JSON format for structured querying
    - Sensitive data should never be logged

"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger


def setup_logging(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    enable_file_logging: bool = True,
) -> None:
    """Configure structured logging for the application.

    Parameters
    ----------
    log_dir
        Directory to store log files
    log_level
        Minimum log level to capture
    enable_file_logging
        Whether to enable file logging

    """
    # Remove default handler
    logger.remove()

    # Create log directory if it doesn't exist
    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)

    # Add console handler with colors
    logger.add(
        sys.stdout,
        level=log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Add file handler with rotation and JSON format
    if enable_file_logging:
        logger.add(
            log_dir / "reddit_wsb_stocks.log",
            level=log_level.upper(),
            rotation="00:00",  # Rotate at midnight
            retention="30 days",  # Keep logs for 30 days
            encoding="utf-8",
            serialize=True,  # JSON format
        )


def get_logger(name: str) -> Any:
    """Get a configured logger instance.

    Parameters
    ----------
    name
        Logger name (typically __name__)

    Returns
    -------
    Any
        Configured logger instance

    """
    return logger.bind(name=name)
