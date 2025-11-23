"""
Title: Tradestie API Client

Author: Claude AI

Description:
HTTP client for interacting with the Tradestie API to retrieve Reddit WSB
stock sentiment data. Uses httpx for async/sync requests and validates
responses using Pydantic models.

Usage:
    from reddit_wsb_stocks.client import TradestieClient

    # Sync usage
    client = TradestieClient()
    data = client.get_stock_sentiment()

    # With specific date
    data = client.get_stock_sentiment(date="11-02-2025")

    # Async usage
    async with TradestieClient() as client:
        data = await client.aget_stock_sentiment()

Notes:
    - API endpoint: https://api.tradestie.com/v1/apps/reddit
    - Date format must be MM-DD-YYYY
    - No authentication required for this public API

"""

import re
from datetime import datetime
from typing import Any

import httpx
from pydantic import ValidationError

from reddit_wsb_stocks.logging_config import get_logger
from reddit_wsb_stocks.models import APIResponse, StockSentiment

logger = get_logger(__name__)


class TradestieAPIError(Exception):
    """Raised when the Tradestie API returns an error."""


class TradestieClient:
    """Client for interacting with the Tradestie Reddit WSB API.

    Attributes
    ----------
    base_url
        Base URL for the Tradestie API
    timeout
        Request timeout in seconds

    """

    BASE_URL = "https://api.tradestie.com/v1/apps/reddit"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Tradestie API client.

        Parameters
        ----------
        timeout
            Request timeout in seconds
        base_url
            Override the default base URL (for testing)

        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

        logger.info(
            "client_initialized",
            base_url=self.base_url,
            timeout=timeout,
        )

    def _get_client(self) -> httpx.Client:
        """Get or create a synchronous HTTP client.

        Returns
        -------
        httpx.Client
            Configured HTTP client

        """
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create an asynchronous HTTP client.

        Returns
        -------
        httpx.AsyncClient
            Configured async HTTP client

        """
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout)
        return self._async_client

    def _validate_date_format(self, date: str) -> None:
        """Validate date string format.

        Parameters
        ----------
        date
            Date string to validate

        Raises
        ------
        ValueError
            If date format is invalid

        """
        # First check strict format with regex (MM-DD-YYYY)
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", date):
            raise ValueError(f"Date must be in MM-DD-YYYY format, got: {date}")

        # Then validate it's a real date
        try:
            datetime.strptime(date, "%m-%d-%Y")
        except ValueError as e:
            raise ValueError(f"Date must be in MM-DD-YYYY format, got: {date}") from e

    def get_stock_sentiment(self, date: str | None = None) -> APIResponse:
        """Fetch stock sentiment data from Reddit WSB.

        Parameters
        ----------
        date
            Optional date in MM-DD-YYYY format. If not provided,
            returns the latest available data.

        Returns
        -------
        APIResponse
            Validated API response containing stock sentiment data

        Raises
        ------
        ValueError
            If date format is invalid
        TradestieAPIError
            If API request fails
        ValidationError
            If response data is invalid

        """
        if date:
            self._validate_date_format(date)

        params: dict[str, str] = {"date": date} if date else {}

        logger.info(
            "fetching_stock_sentiment",
            date=date or "latest",
            url=self.base_url,
        )

        try:
            client = self._get_client()
            response = client.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            logger.info(
                "stock_sentiment_fetched",
                status_code=response.status_code,
                num_stocks=len(data),
                date=date,
            )

            # Validate response data
            stock_sentiments = [StockSentiment.model_validate(item) for item in data]

            return APIResponse(
                data=stock_sentiments,
                date_requested=date,
            )

        except httpx.HTTPError as e:
            logger.error(
                "api_request_failed",
                error=str(e),
                url=self.base_url,
                date=date,
                exc_info=True,
            )
            raise TradestieAPIError(
                f"Failed to fetch data from Tradestie API: {e}"
            ) from e

        except ValidationError as e:
            logger.error(
                "response_validation_failed",
                error=str(e),
                exc_info=True,
            )
            raise

    async def aget_stock_sentiment(self, date: str | None = None) -> APIResponse:
        """Async: Fetch stock sentiment data from Reddit WSB.

        Parameters
        ----------
        date
            Optional date in MM-DD-YYYY format. If not provided,
            returns the latest available data.

        Returns
        -------
        APIResponse
            Validated API response containing stock sentiment data

        Raises
        ------
        ValueError
            If date format is invalid
        TradestieAPIError
            If API request fails
        ValidationError
            If response data is invalid

        """
        if date:
            self._validate_date_format(date)

        params: dict[str, str] = {"date": date} if date else {}

        logger.info(
            "fetching_stock_sentiment_async",
            date=date or "latest",
            url=self.base_url,
        )

        try:
            client = self._get_async_client()
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            logger.info(
                "stock_sentiment_fetched_async",
                status_code=response.status_code,
                num_stocks=len(data),
                date=date,
            )

            # Validate response data
            stock_sentiments = [StockSentiment.model_validate(item) for item in data]

            return APIResponse(
                data=stock_sentiments,
                date_requested=date,
            )

        except httpx.HTTPError as e:
            logger.error(
                "api_request_failed_async",
                error=str(e),
                url=self.base_url,
                date=date,
                exc_info=True,
            )
            raise TradestieAPIError(
                f"Failed to fetch data from Tradestie API: {e}"
            ) from e

        except ValidationError as e:
            logger.error(
                "response_validation_failed_async",
                error=str(e),
                exc_info=True,
            )
            raise

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            self._client.close()
            self._client = None
        logger.debug("client_closed")

    async def aclose(self) -> None:
        """Async: Close the HTTP client and release resources."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
        logger.debug("async_client_closed")

    def __enter__(self) -> "TradestieClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "TradestieClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
