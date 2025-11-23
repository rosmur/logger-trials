"""Tests for CLI functionality."""

from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from reddit_wsb_stocks.cli import main, parse_args


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
    ]


class TestParseArgs:
    """Tests for command line argument parsing."""

    def test_parse_args_defaults(self) -> None:
        """Test default argument values."""
        args = parse_args([])

        assert args.date is None
        assert args.output == "data"
        assert args.filename is None
        assert args.log_level == "INFO"
        assert args.no_file_logs is False

    def test_parse_args_with_date(self) -> None:
        """Test parsing with date argument."""
        args = parse_args(["--date", "11-02-2025"])

        assert args.date == "11-02-2025"

    def test_parse_args_with_output(self) -> None:
        """Test parsing with custom output directory."""
        args = parse_args(["--output", "my_data"])

        assert args.output == "my_data"

    def test_parse_args_with_filename(self) -> None:
        """Test parsing with custom filename."""
        args = parse_args(["--filename", "stocks.json"])

        assert args.filename == "stocks.json"

    def test_parse_args_with_log_level(self) -> None:
        """Test parsing with different log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            args = parse_args(["--log-level", level])
            assert args.log_level == level

    def test_parse_args_no_file_logs(self) -> None:
        """Test parsing --no-file-logs flag."""
        args = parse_args(["--no-file-logs"])

        assert args.no_file_logs is True

    def test_parse_args_combined(self) -> None:
        """Test parsing multiple arguments together."""
        args = parse_args(
            [
                "--date",
                "11-02-2025",
                "--output",
                "data/stocks",
                "--filename",
                "my_stocks.json",
                "--log-level",
                "DEBUG",
                "--no-file-logs",
            ]
        )

        assert args.date == "11-02-2025"
        assert args.output == "data/stocks"
        assert args.filename == "my_stocks.json"
        assert args.log_level == "DEBUG"
        assert args.no_file_logs is True


class TestMainCLI:
    """Tests for main CLI function."""

    def test_main_success(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        sample_api_response: list[dict],
    ) -> None:
        """Test successful CLI execution."""
        httpx_mock.add_response(json=sample_api_response)

        exit_code = main(["--output", str(tmp_path), "--no-file-logs"])

        assert exit_code == 0

        # Check that file was created
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1

    def test_main_with_date(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        sample_api_response: list[dict],
    ) -> None:
        """Test CLI with specific date."""
        httpx_mock.add_response(json=sample_api_response)

        exit_code = main(
            [
                "--date",
                "11-02-2025",
                "--output",
                str(tmp_path),
                "--no-file-logs",
            ]
        )

        assert exit_code == 0

    def test_main_with_custom_filename(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        sample_api_response: list[dict],
    ) -> None:
        """Test CLI with custom filename."""
        httpx_mock.add_response(json=sample_api_response)

        exit_code = main(
            [
                "--output",
                str(tmp_path),
                "--filename",
                "custom.json",
                "--no-file-logs",
            ]
        )

        assert exit_code == 0

        # Check that file has correct name
        filepath = tmp_path / "custom.json"
        assert filepath.exists()

    def test_main_invalid_date(self, tmp_path: Path) -> None:
        """Test CLI with invalid date format."""
        exit_code = main(
            [
                "--date",
                "2025-11-02",  # Wrong format
                "--output",
                str(tmp_path),
                "--no-file-logs",
            ]
        )

        assert exit_code == 1

    def test_main_api_error(self, tmp_path: Path, httpx_mock: HTTPXMock) -> None:
        """Test CLI handling of API errors."""
        httpx_mock.add_response(status_code=500)

        exit_code = main(["--output", str(tmp_path), "--no-file-logs"])

        assert exit_code == 1
