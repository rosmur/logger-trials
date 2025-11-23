"""
Title: Reddit WSB Stocks - Main Package

Author: Claude AI

Description:
Python package for retrieving Reddit WSB stock sentiment data from the
Tradestie API and saving it to JSON files.

Usage:
    # Use the client directly
    from reddit_wsb_stocks import TradestieClient, save_to_json

    client = TradestieClient()
    response = client.get_stock_sentiment()
    filepath = save_to_json(response)

    # Or use the CLI
    python -m reddit_wsb_stocks --date 11-02-2025

Notes:
    - All data is validated using Pydantic models
    - Structured logging with structlog
    - Type-safe with full type annotations

"""

from reddit_wsb_stocks.client import TradestieAPIError, TradestieClient
from reddit_wsb_stocks.models import APIResponse, StockSentiment
from reddit_wsb_stocks.storage import StorageError, load_from_json, save_to_json

__version__ = "0.1.0"

__all__ = [
    "TradestieClient",
    "TradestieAPIError",
    "StockSentiment",
    "APIResponse",
    "save_to_json",
    "load_from_json",
    "StorageError",
]
