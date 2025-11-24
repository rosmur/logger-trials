"""
Title: Logging Configuration Settings

Author: Claude AI

Description:
Centralized logging configuration dictionary for use with logging.config.dictConfig().
Defines handlers, formatters, and loggers in a structured format.

"""

from pathlib import Path
from typing import Any


def get_logging_config(
    log_dir: Path = Path("logs"),
    log_level: str = "INFO",
    enable_file_logging: bool = True,
) -> dict[str, Any]:
    """Get logging configuration dictionary for dictConfig.

    Parameters
    ----------
    log_dir
        Directory to store log files
    log_level
        Minimum log level to capture
    enable_file_logging
        Whether to enable file logging

    Returns
    -------
    dict[str, Any]
        Logging configuration dictionary

    """
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored_console": {
                "()": "reddit_wsb_stocks.logging_config.ColoredConsoleFormatter",
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "reddit_wsb_stocks.logging_config.JSONFormatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level.upper(),
                "formatter": "colored_console",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level.upper(),
            "handlers": ["console"],
        },
    }

    # Add file handler if enabled
    if enable_file_logging:
        log_file_path = str(log_dir / "reddit_wsb_stocks.log")

        config["handlers"]["file"] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": log_level.upper(),
            "formatter": "json",
            "filename": log_file_path,
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        }

        # Add file handler to root logger
        config["root"]["handlers"].append("file")

    return config
