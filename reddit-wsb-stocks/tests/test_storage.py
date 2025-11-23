"""Tests for storage functionality."""

import json
from pathlib import Path

import pytest

from reddit_wsb_stocks.models import APIResponse, StockSentiment
from reddit_wsb_stocks.storage import (
    load_from_json,
    save_to_json,
)


@pytest.fixture
def sample_response() -> APIResponse:
    """Create a sample APIResponse for testing."""
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
    return APIResponse(data=stocks, date_requested="11-02-2025")


class TestSaveToJSON:
    """Tests for save_to_json function."""

    def test_save_to_json_default_filename(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test saving with auto-generated filename."""
        filepath = save_to_json(sample_response, output_dir=tmp_path)

        assert filepath.exists()
        assert filepath.suffix == ".json"
        assert filepath.name.startswith("wsb_stocks_")
        assert filepath.parent == tmp_path

    def test_save_to_json_custom_filename(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test saving with custom filename."""
        filepath = save_to_json(
            sample_response,
            output_dir=tmp_path,
            filename="my_data.json",
        )

        assert filepath.exists()
        assert filepath.name == "my_data.json"

    def test_save_to_json_adds_json_extension(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that .json extension is added if missing."""
        filepath = save_to_json(
            sample_response,
            output_dir=tmp_path,
            filename="my_data",
        )

        assert filepath.name == "my_data.json"

    def test_save_to_json_creates_directory(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that output directory is created if it doesn't exist."""
        nested_dir = tmp_path / "nested" / "path"
        filepath = save_to_json(sample_response, output_dir=nested_dir)

        assert nested_dir.exists()
        assert filepath.exists()

    def test_save_to_json_content(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that JSON content is correct."""
        filepath = save_to_json(sample_response, output_dir=tmp_path)

        with filepath.open("r") as f:
            data = json.load(f)

        assert "fetched_at" in data
        assert "date_requested" in data
        assert "count" in data
        assert "stocks" in data

        assert data["date_requested"] == "11-02-2025"
        assert data["count"] == 2
        assert len(data["stocks"]) == 2

        assert data["stocks"][0]["ticker"] == "GME"
        assert data["stocks"][0]["sentiment"] == "Bullish"
        assert data["stocks"][0]["no_of_comments"] == 179

    def test_save_to_json_pretty_formatting(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that pretty formatting works."""
        filepath = save_to_json(sample_response, output_dir=tmp_path, pretty=True)

        content = filepath.read_text()

        # Pretty formatted JSON should have newlines and indentation
        assert "\n" in content
        assert "  " in content

    def test_save_to_json_compact_formatting(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test compact (non-pretty) formatting."""
        filepath = save_to_json(sample_response, output_dir=tmp_path, pretty=False)

        content = filepath.read_text()

        # Should be more compact (but may still have some newlines)
        pretty_filepath = save_to_json(
            sample_response,
            output_dir=tmp_path,
            filename="pretty.json",
            pretty=True,
        )
        pretty_content = pretty_filepath.read_text()

        assert len(content) <= len(pretty_content)


class TestLoadFromJSON:
    """Tests for load_from_json function."""

    def test_load_from_json_success(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test successfully loading JSON file."""
        # Save first
        filepath = save_to_json(sample_response, output_dir=tmp_path)

        # Load it back
        loaded = load_from_json(filepath)

        assert isinstance(loaded, APIResponse)
        assert len(loaded.data) == len(sample_response.data)
        assert loaded.data[0].ticker == sample_response.data[0].ticker
        assert loaded.date_requested == sample_response.date_requested

    def test_load_from_json_file_not_found(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing files."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="File not found"):
            load_from_json(nonexistent)

    def test_load_from_json_invalid_json(self, tmp_path: Path) -> None:
        """Test handling of invalid JSON."""
        filepath = tmp_path / "invalid.json"
        filepath.write_text("not valid json{")

        with pytest.raises(ValueError, match="Invalid JSON data"):
            load_from_json(filepath)

    def test_load_from_json_missing_fields(self, tmp_path: Path) -> None:
        """Test handling of JSON with missing required fields."""
        filepath = tmp_path / "incomplete.json"
        filepath.write_text('{"count": 0}')

        with pytest.raises(ValueError, match="Invalid JSON data"):
            load_from_json(filepath)

    def test_roundtrip_save_load(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that save and load are symmetric."""
        filepath = save_to_json(sample_response, output_dir=tmp_path)
        loaded = load_from_json(filepath)

        # Compare key fields
        assert len(loaded.data) == len(sample_response.data)
        for original, loaded_stock in zip(
            sample_response.data, loaded.data, strict=True
        ):
            assert loaded_stock.ticker == original.ticker
            assert loaded_stock.sentiment == original.sentiment
            assert loaded_stock.sentiment_score == original.sentiment_score
            assert loaded_stock.no_of_comments == original.no_of_comments


class TestStorageEdgeCases:
    """Tests for edge cases and error handling."""

    def test_save_with_empty_stock_list(self, tmp_path: Path) -> None:
        """Test saving response with no stocks."""
        response = APIResponse(data=[])
        filepath = save_to_json(response, output_dir=tmp_path)

        assert filepath.exists()

        with filepath.open("r") as f:
            data = json.load(f)

        assert data["count"] == 0
        assert data["stocks"] == []

    def test_save_with_string_path(
        self, tmp_path: Path, sample_response: APIResponse
    ) -> None:
        """Test that string paths are handled correctly."""
        filepath = save_to_json(sample_response, output_dir=str(tmp_path))

        assert isinstance(filepath, Path)
        assert filepath.exists()
