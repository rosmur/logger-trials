"""Tests for data models."""

from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from reddit_wsb_stocks.models import APIResponse, StockSentiment


class TestStockSentiment:
    """Tests for StockSentiment model."""

    @pytest.mark.parametrize(
        "ticker,sentiment,score,comments",
        [
            ("GME", "Bullish", 0.13, 179),
            ("AMC", "Bearish", -0.5, 37),
            ("PLTR", "Neutral", 0.0, 17),
        ],
    )
    def test_valid_stock_sentiment(
        self, ticker: str, sentiment: str, score: float, comments: int
    ) -> None:
        """Test creating valid StockSentiment instances."""
        stock = StockSentiment(
            ticker=ticker,
            sentiment=sentiment,
            sentiment_score=score,
            no_of_comments=comments,
        )

        assert stock.ticker == ticker.upper()
        assert stock.sentiment == sentiment
        assert stock.sentiment_score == score
        assert stock.no_of_comments == comments

    def test_ticker_uppercase_conversion(self) -> None:
        """Test that ticker symbols are converted to uppercase."""
        stock = StockSentiment(
            ticker="gme",
            sentiment="Bullish",
            sentiment_score=0.5,
            no_of_comments=100,
        )
        assert stock.ticker == "GME"

    def test_ticker_whitespace_stripped(self) -> None:
        """Test that ticker whitespace is stripped."""
        stock = StockSentiment(
            ticker="  GME  ",
            sentiment="Bullish",
            sentiment_score=0.5,
            no_of_comments=100,
        )
        assert stock.ticker == "GME"

    @pytest.mark.parametrize(
        "invalid_sentiment",
        ["bullish", "BULLISH", "positive", "negative", ""],
    )
    def test_invalid_sentiment(self, invalid_sentiment: str) -> None:
        """Test that invalid sentiment values are rejected."""
        with pytest.raises(ValidationError):
            StockSentiment(
                ticker="GME",
                sentiment=invalid_sentiment,
                sentiment_score=0.5,
                no_of_comments=100,
            )

    @pytest.mark.parametrize(
        "invalid_score",
        [-1.1, 1.1, -2.0, 2.0, 10.0],
    )
    def test_sentiment_score_bounds(self, invalid_score: float) -> None:
        """Test that sentiment scores outside [-1, 1] are rejected."""
        with pytest.raises(ValidationError):
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=invalid_score,
                no_of_comments=100,
            )

    def test_negative_comments_rejected(self) -> None:
        """Test that negative comment counts are rejected."""
        with pytest.raises(ValidationError):
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=0.5,
                no_of_comments=-1,
            )

    def test_empty_ticker_rejected(self) -> None:
        """Test that empty ticker strings are rejected."""
        with pytest.raises(ValidationError):
            StockSentiment(
                ticker="",
                sentiment="Bullish",
                sentiment_score=0.5,
                no_of_comments=100,
            )

    @given(
        ticker=st.text(min_size=1, max_size=10),
        score=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        comments=st.integers(min_value=0, max_value=10000),
    )
    def test_random_valid_inputs(
        self, ticker: str, score: float, comments: int
    ) -> None:
        """Test with randomized valid inputs using Hypothesis."""
        stock = StockSentiment(
            ticker=ticker,
            sentiment="Bullish",
            sentiment_score=score,
            no_of_comments=comments,
        )
        assert stock.ticker == ticker.upper().strip()
        assert stock.sentiment_score == score
        assert stock.no_of_comments == comments


class TestAPIResponse:
    """Tests for APIResponse model."""

    def test_valid_api_response(self) -> None:
        """Test creating a valid APIResponse."""
        stocks = [
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=0.13,
                no_of_comments=179,
            ),
            StockSentiment(
                ticker="AMC",
                sentiment="Bearish",
                sentiment_score=-0.2,
                no_of_comments=37,
            ),
        ]

        response = APIResponse(data=stocks, date_requested="11-02-2025")

        assert len(response.data) == 2
        assert response.date_requested == "11-02-2025"
        assert isinstance(response.fetched_at, datetime)

    def test_api_response_without_date(self) -> None:
        """Test APIResponse without a specific date (latest data)."""
        stocks = [
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=0.13,
                no_of_comments=179,
            )
        ]

        response = APIResponse(data=stocks)

        assert response.date_requested is None
        assert isinstance(response.fetched_at, datetime)

    @pytest.mark.parametrize(
        "valid_date",
        ["01-15-2025", "12-31-2024", "06-01-2025"],
    )
    def test_valid_date_formats(self, valid_date: str) -> None:
        """Test valid date formats are accepted."""
        stocks = [
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=0.13,
                no_of_comments=179,
            )
        ]

        response = APIResponse(data=stocks, date_requested=valid_date)
        assert response.date_requested == valid_date

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2025-11-02",  # Wrong format (YYYY-MM-DD)
            "11/02/2025",  # Wrong separator
            "11-2-2025",  # Single digit day
            "1-02-2025",  # Single digit month
            "13-01-2025",  # Invalid month
            "11-32-2025",  # Invalid day
            "not-a-date",
        ],
    )
    def test_invalid_date_formats(self, invalid_date: str) -> None:
        """Test invalid date formats are rejected."""
        stocks = [
            StockSentiment(
                ticker="GME",
                sentiment="Bullish",
                sentiment_score=0.13,
                no_of_comments=179,
            )
        ]

        with pytest.raises(ValidationError):
            APIResponse(data=stocks, date_requested=invalid_date)

    def test_empty_stock_list(self) -> None:
        """Test APIResponse with empty stock list."""
        response = APIResponse(data=[])
        assert len(response.data) == 0
