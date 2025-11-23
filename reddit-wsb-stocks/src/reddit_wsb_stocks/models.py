"""
Title: Data Models for Reddit WSB Stock Data

Author: Claude AI

Description:
Pydantic models for validating and structuring stock sentiment data from the
Tradestie API. These models ensure type safety and data validation at system
boundaries.

Usage:
    from reddit_wsb_stocks.models import StockSentiment

    data = {
        "ticker": "GME",
        "sentiment": "Bullish",
        "sentiment_score": 0.13,
        "no_of_comments": 179
    }
    stock = StockSentiment.model_validate(data)

Notes:
    - All fields are required as per API specification
    - Sentiment must be one of: Bullish, Bearish, or Neutral
    - Sentiment score is a float between -1.0 and 1.0
"""

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class StockSentiment(BaseModel):
    """Model representing sentiment data for a single stock ticker.

    Attributes
    ----------
    ticker
        Stock ticker symbol (e.g., 'GME', 'AMC')
    sentiment
        Overall sentiment classification
    sentiment_score
        Numerical sentiment score, typically between -1.0 and 1.0
    no_of_comments
        Number of comments mentioning this ticker

    """

    ticker: str = Field(..., min_length=1, description="Stock ticker symbol")
    sentiment: Literal["Bullish", "Bearish", "Neutral"] = Field(
        ..., description="Overall sentiment classification"
    )
    sentiment_score: float = Field(
        ..., ge=-1.0, le=1.0, description="Numerical sentiment score"
    )
    no_of_comments: int = Field(
        ..., ge=0, description="Number of comments mentioning this ticker"
    )

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Ensure ticker symbols are uppercase.

        Parameters
        ----------
        v
            The ticker symbol to validate

        Returns
        -------
        str
            Uppercase ticker symbol

        """
        return v.upper().strip()


class APIResponse(BaseModel):
    """Model for the complete API response.

    Attributes
    ----------
    data
        List of stock sentiment data
    fetched_at
        Timestamp when data was fetched
    date_requested
        The date that was requested (None for latest)

    """

    data: list[StockSentiment] = Field(..., description="List of stock sentiment data")
    fetched_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when data was fetched"
    )
    date_requested: str | None = Field(
        None, description="The date that was requested (MM-DD-YYYY format)"
    )

    @field_validator("date_requested")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate date format is MM-DD-YYYY.

        Parameters
        ----------
        v
            Date string to validate

        Returns
        -------
        str | None
            Validated date string or None

        Raises
        ------
        ValueError
            If date format is invalid

        """
        if v is None:
            return v

        # First check strict format with regex (MM-DD-YYYY)
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", v):
            raise ValueError(f"Date must be in MM-DD-YYYY format, got: {v}")

        # Then validate it's a real date
        try:
            datetime.strptime(v, "%m-%d-%Y")
            return v
        except ValueError as e:
            raise ValueError(f"Date must be in MM-DD-YYYY format, got: {v}") from e
