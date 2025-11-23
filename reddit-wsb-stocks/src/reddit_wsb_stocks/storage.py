"""
Title: JSON Storage Manager

Author: Claude AI

Description:
Handles saving Reddit WSB stock sentiment data to JSON files with proper
file naming, validation, and error handling.

Usage:
    from reddit_wsb_stocks.storage import save_to_json
    from reddit_wsb_stocks.models import APIResponse

    response = APIResponse(...)
    filepath = save_to_json(response, output_dir="data")

Notes:
    - Files are named with timestamp: wsb_stocks_YYYYMMDD_HHMMSS.json
    - Custom filenames can be provided
    - Directory structure is created automatically
    - Data is validated before saving

"""

import json
from datetime import datetime
from pathlib import Path

from reddit_wsb_stocks.logging_config import get_logger
from reddit_wsb_stocks.models import APIResponse

logger = get_logger(__name__)


class StorageError(Exception):
    """Raised when storage operations fail."""


def save_to_json(
    data: APIResponse,
    output_dir: Path | str = Path("data"),
    filename: str | None = None,
    pretty: bool = True,
) -> Path:
    """Save stock sentiment data to a JSON file.

    Parameters
    ----------
    data
        Validated API response to save
    output_dir
        Directory to save the file in
    filename
        Optional custom filename. If not provided, generates a
        timestamped filename: wsb_stocks_YYYYMMDD_HHMMSS.json
    pretty
        Whether to format JSON with indentation

    Returns
    -------
    Path
        Path to the saved file

    Raises
    ------
    StorageError
        If file operations fail
    ValueError
        If data is invalid

    """
    # Convert to Path object
    output_dir = Path(output_dir)

    # Validate output directory path
    try:
        output_dir = output_dir.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid output directory path: {output_dir}") from e

    # Create directory if it doesn't exist
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("output_directory_created", path=str(output_dir))
    except OSError as e:
        logger.error(
            "failed_to_create_directory",
            path=str(output_dir),
            error=str(e),
            exc_info=True,
        )
        raise StorageError(f"Failed to create directory {output_dir}: {e}") from e

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wsb_stocks_{timestamp}.json"

    # Ensure filename has .json extension
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    filepath = output_dir / filename

    # Prepare data for JSON serialization
    json_data = {
        "fetched_at": data.fetched_at.isoformat(),
        "date_requested": data.date_requested,
        "count": len(data.data),
        "stocks": [stock.model_dump() for stock in data.data],
    }

    # Save to file
    try:
        with filepath.open("w", encoding="utf-8") as f:
            if pretty:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(json_data, f, ensure_ascii=False)

        logger.info(
            "data_saved_to_json",
            filepath=str(filepath),
            num_stocks=len(data.data),
            size_bytes=filepath.stat().st_size,
        )

        return filepath

    except OSError as e:
        logger.error(
            "failed_to_save_json",
            filepath=str(filepath),
            error=str(e),
            exc_info=True,
        )
        raise StorageError(f"Failed to save data to {filepath}: {e}") from e


def load_from_json(filepath: Path | str) -> APIResponse:
    """Load stock sentiment data from a JSON file.

    Parameters
    ----------
    filepath
        Path to the JSON file to load

    Returns
    -------
    APIResponse
        Loaded and validated API response

    Raises
    ------
    StorageError
        If file operations fail
    FileNotFoundError
        If file doesn't exist
    ValueError
        If JSON data is invalid

    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with filepath.open("r", encoding="utf-8") as f:
            json_data = json.load(f)

        logger.info("data_loaded_from_json", filepath=str(filepath))

        # Reconstruct APIResponse
        response = APIResponse(
            data=json_data["stocks"],
            fetched_at=datetime.fromisoformat(json_data["fetched_at"]),
            date_requested=json_data.get("date_requested"),
        )

        return response

    except OSError as e:
        logger.error(
            "failed_to_load_json",
            filepath=str(filepath),
            error=str(e),
            exc_info=True,
        )
        raise StorageError(f"Failed to load data from {filepath}: {e}") from e

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(
            "invalid_json_data",
            filepath=str(filepath),
            error=str(e),
            exc_info=True,
        )
        raise ValueError(f"Invalid JSON data in {filepath}: {e}") from e
