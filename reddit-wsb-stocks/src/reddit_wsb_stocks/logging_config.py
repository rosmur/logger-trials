"""
Title: Python Logging Configuration

Author: Claude AI

Description:
Centralized logging configuration using Python's built-in logging module with
colored output and file rotation. Uses logging.config.dictConfig() with settings
from logging_settings.py for better separation of concerns.

Usage:
    from reddit_wsb_stocks.logging_config import setup_logging, get_logger

    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application started", extra={"version": "1.0.0"})

Notes:
    - Logs are rotated daily and kept for 30 days
    - Console output includes colored level names
    - File output uses JSON format for structured querying
    - Sensitive data should never be logged
    - Configuration is defined in logging_settings.py

"""

import json
import logging
import logging.config
from pathlib import Path
from typing import Any

from colorama import Fore, Style, init

from reddit_wsb_stocks.logging_settings import get_logging_config

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


class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels in console output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colored level name.

        Parameters
        ----------
        record
            The log record to format

        Returns
        -------
        str
            Formatted log message with colored level

        """
        # Save original levelname
        original_levelname = record.levelname

        # Add color to levelname
        if record.levelname in LEVEL_COLORS:
            record.levelname = (
                f"{LEVEL_COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
            )

        # Format the message
        result = super().format(record)

        # Restore original levelname
        record.levelname = original_levelname

        return result


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON for file logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Parameters
        ----------
        record
            The log record to format

        Returns
        -------
        str
            JSON formatted log message

        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add stack info if present
        if record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_data)


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that allows structlog-style logging with keyword arguments.

    This adapter mimics structlog's API by accepting arbitrary keyword arguments
    and converting them to Python logging's extra parameter format.
    """

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Process log message and convert kwargs to extra parameter.

        Parameters
        ----------
        msg
            The log message
        kwargs
            Additional keyword arguments

        Returns
        -------
        tuple[str, dict[str, Any]]
            Processed message and kwargs

        """
        # Standard logging kwargs that should not be moved to extra
        standard_kwargs = {"exc_info", "stack_info", "stacklevel", "extra"}

        # Separate standard kwargs from context kwargs
        extra_data = {}
        cleaned_kwargs = {}

        for key, value in kwargs.items():
            if key in standard_kwargs:
                cleaned_kwargs[key] = value
            else:
                # All other kwargs become extra data
                extra_data[key] = value

        # Merge with existing extra if present
        if "extra" in cleaned_kwargs:
            existing_extra = cleaned_kwargs["extra"]
            if isinstance(existing_extra, dict):
                extra_data.update(existing_extra)

        # Set the extra data in a way JSONFormatter can access
        if extra_data:
            cleaned_kwargs["extra"] = {"extra_data": extra_data}

        return msg, cleaned_kwargs


def setup_logging(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    enable_file_logging: bool = True,
) -> None:
    """Configure logging for the application using dictConfig.

    Parameters
    ----------
    log_dir
        Directory to store log files
    log_level
        Minimum log level to capture
    enable_file_logging
        Whether to enable file logging

    Notes
    -----
    This function uses logging.config.dictConfig() with configuration
    defined in logging_settings.py for better separation of concerns.

    """
    # Create log directory if it doesn't exist
    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)

    # Get logging configuration from settings
    config = get_logging_config(
        log_dir=log_dir,
        log_level=log_level,
        enable_file_logging=enable_file_logging,
    )

    # Apply configuration using dictConfig
    logging.config.dictConfig(config)


def get_logger(name: str) -> ContextLogger:
    """Get a configured logger instance.

    Parameters
    ----------
    name
        Logger name (typically __name__)

    Returns
    -------
    ContextLogger
        Configured logger instance that supports context via extra parameter

    """
    logger = logging.getLogger(name)
    return ContextLogger(logger, {})
