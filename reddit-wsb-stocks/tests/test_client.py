"""Tests for API client."""

import pytest
from pydantic import ValidationError
from pytest_httpx import HTTPXMock

from reddit_wsb_stocks.client import TradestieAPIError, TradestieClient
from reddit_wsb_stocks.models import APIResponse


@pytest.fixture
def sample_api_response() -> list[dict]:
    """Sample API response data."""
    return [
        {
            "ticker": "GME",
            "sentiment": "Bullish",
            "sentiment_score": 0.13,
            "no_of_comments": 179,
        },
        {
            "ticker": "AMC",
            "sentiment": "Bullish",
            "sentiment_score": 0.159,
            "no_of_comments": 37,
        },
        {
            "ticker": "PLTR",
            "sentiment": "Bullish",
            "sentiment_score": 0.22,
            "no_of_comments": 17,
        },
    ]


class TestTradestieClient:
    """Tests for TradestieClient."""

    def test_client_initialization(self) -> None:
        """Test client is initialized correctly."""
        client = TradestieClient()
        assert client.base_url == TradestieClient.BASE_URL
        assert client.timeout == TradestieClient.DEFAULT_TIMEOUT

    def test_client_custom_timeout(self) -> None:
        """Test client with custom timeout."""
        client = TradestieClient(timeout=60.0)
        assert client.timeout == 60.0

    def test_client_custom_base_url(self) -> None:
        """Test client with custom base URL."""
        custom_url = "https://example.com/api"
        client = TradestieClient(base_url=custom_url)
        assert client.base_url == custom_url

    def test_get_stock_sentiment_success(
        self, httpx_mock: HTTPXMock, sample_api_response: list[dict]
    ) -> None:
        """Test successful stock sentiment retrieval."""
        httpx_mock.add_response(json=sample_api_response)

        client = TradestieClient()
        response = client.get_stock_sentiment()

        assert isinstance(response, APIResponse)
        assert len(response.data) == 3
        assert response.data[0].ticker == "GME"
        assert response.data[0].no_of_comments == 179
        assert response.date_requested is None

    def test_get_stock_sentiment_with_date(
        self, httpx_mock: HTTPXMock, sample_api_response: list[dict]
    ) -> None:
        """Test stock sentiment retrieval with specific date."""
        httpx_mock.add_response(json=sample_api_response)

        client = TradestieClient()
        response = client.get_stock_sentiment(date="11-02-2025")

        assert isinstance(response, APIResponse)
        assert response.date_requested == "11-02-2025"

        # Verify request was made with correct parameters
        request = httpx_mock.get_request()
        assert request is not None
        assert "date=11-02-2025" in str(request.url)

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2025-11-02",
            "11/02/2025",
            "invalid",
            "13-01-2025",
        ],
    )
    def test_get_stock_sentiment_invalid_date(self, invalid_date: str) -> None:
        """Test that invalid dates raise ValueError."""
        client = TradestieClient()

        with pytest.raises(ValueError, match="Date must be in MM-DD-YYYY format"):
            client.get_stock_sentiment(date=invalid_date)

    def test_get_stock_sentiment_http_error(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of HTTP errors."""
        httpx_mock.add_response(status_code=500)

        client = TradestieClient()

        with pytest.raises(TradestieAPIError, match="Failed to fetch data"):
            client.get_stock_sentiment()

    def test_get_stock_sentiment_invalid_response(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of invalid API response."""
        # Missing required fields
        invalid_response = [
            {
                "ticker": "GME",
                "sentiment": "Bullish",
                # Missing sentiment_score and no_of_comments
            }
        ]

        httpx_mock.add_response(json=invalid_response)

        client = TradestieClient()

        with pytest.raises(ValidationError):
            client.get_stock_sentiment()

    def test_context_manager(
        self, httpx_mock: HTTPXMock, sample_api_response: list[dict]
    ) -> None:
        """Test using client as context manager."""
        httpx_mock.add_response(json=sample_api_response)

        with TradestieClient() as client:
            response = client.get_stock_sentiment()
            assert len(response.data) == 3

    @pytest.mark.asyncio
    async def test_async_get_stock_sentiment(
        self, httpx_mock: HTTPXMock, sample_api_response: list[dict]
    ) -> None:
        """Test async stock sentiment retrieval."""
        httpx_mock.add_response(json=sample_api_response)

        async with TradestieClient() as client:
            response = await client.aget_stock_sentiment()
            assert isinstance(response, APIResponse)
            assert len(response.data) == 3

    @pytest.mark.asyncio
    async def test_async_get_stock_sentiment_with_date(
        self, httpx_mock: HTTPXMock, sample_api_response: list[dict]
    ) -> None:
        """Test async retrieval with specific date."""
        httpx_mock.add_response(json=sample_api_response)

        async with TradestieClient() as client:
            response = await client.aget_stock_sentiment(date="11-02-2025")
            assert response.date_requested == "11-02-2025"
