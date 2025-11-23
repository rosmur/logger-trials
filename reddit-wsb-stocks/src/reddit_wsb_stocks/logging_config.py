"""
Title: Structured Logging Configuration

Author: Claude AI

Description:
Centralized logging configuration using structlog with colored output and file
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

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

import structlog
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Color mapping for log levels
LEVEL_COLORS = {
    "CRITICAL": Fore.RED + Style.BRIGHT,
    "ERROR": Fore.LIGHTRED_EX,
    "WARNING": Fore.YELLOW,
    "INFO": Fore.BLUE,
    "DEBUG": Fore.LIGHTBLACK_EX,
}


def add_log_level_color(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add color to log level names in console output.

    Parameters
    ----------
    logger
        The logger instance
    method_name
        The name of the method being called
    event_dict
        The event dictionary containing log data

    Returns
    -------
    dict[str, Any]
        Event dictionary with colored level

    """
    level = event_dict.get("level", "").upper()
    if level in LEVEL_COLORS:
        event_dict["level"] = f"{LEVEL_COLORS[level]}{level}{Style.RESET_ALL}"
    return event_dict


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
    # Create log directory if it doesn't exist
    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Set up structlog processors
    processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # File handler with rotation
    file_handler: TimedRotatingFileHandler | None = None
    if enable_file_logging:
        file_handler = TimedRotatingFileHandler(
            filename=log_dir / "reddit_wsb_stocks.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

    # Configure structlog
    structlog.configure(
        processors=processors
        + [
            add_log_level_color,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up formatters
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=False),
        foreign_pre_chain=processors,
    )

    console_handler.setFormatter(console_formatter)

    if enable_file_logging and file_handler is not None:
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=processors,
        )
        file_handler.setFormatter(file_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    if enable_file_logging and file_handler is not None:
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Parameters
    ----------
    name
        Logger name (typically __name__)

    Returns
    -------
    structlog.stdlib.BoundLogger
        Configured logger instance

    """
    return structlog.get_logger(name)
