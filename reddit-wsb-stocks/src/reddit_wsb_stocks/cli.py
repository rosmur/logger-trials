"""
Title: Command Line Interface

Author: Claude AI

Description:
Command-line interface for fetching Reddit WSB stock sentiment data and
saving it to JSON files.

Usage:
    # Get latest data
    python -m reddit_wsb_stocks

    # Get data for specific date
    python -m reddit_wsb_stocks --date 11-02-2025

    # Specify output directory
    python -m reddit_wsb_stocks --output data/stocks

    # Custom filename
    python -m reddit_wsb_stocks --filename my_data.json

Notes:
    - Date must be in MM-DD-YYYY format
    - Output directory is created if it doesn't exist
    - Logging level can be adjusted with --log-level

"""

import argparse
import sys

from reddit_wsb_stocks.client import TradestieAPIError, TradestieClient
from reddit_wsb_stocks.logging_config import get_logger, setup_logging
from reddit_wsb_stocks.storage import StorageError, save_to_json


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Parameters
    ----------
    args
        Command line arguments (None uses sys.argv)

    Returns
    -------
    argparse.Namespace
        Parsed arguments

    """
    parser = argparse.ArgumentParser(
        description="Fetch Reddit WSB stock sentiment data from Tradestie API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Date in MM-DD-YYYY format (e.g., 11-02-2025). "
        "If not provided, fetches latest data.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="data",
        help="Output directory for JSON files (default: data)",
    )

    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        help="Custom filename for output (default: auto-generated with timestamp)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--no-file-logs",
        action="store_true",
        help="Disable file logging (console only)",
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point.

    Parameters
    ----------
    args
        Command line arguments (None uses sys.argv)

    Returns
    -------
    int
        Exit code (0 for success, 1 for error)

    """
    parsed_args = parse_args(args)

    # Setup logging
    setup_logging(
        log_level=parsed_args.log_level,
        enable_file_logging=not parsed_args.no_file_logs,
    )

    logger = get_logger(__name__)

    logger.info(
        "cli_started",
        date=parsed_args.date or "latest",
        output_dir=parsed_args.output,
        filename=parsed_args.filename,
    )

    try:
        # Fetch data from API
        with TradestieClient() as client:
            logger.info("fetching_data_from_api")
            response = client.get_stock_sentiment(date=parsed_args.date)

        # Display summary
        print(f"\n✓ Successfully fetched {len(response.data)} stocks")
        if response.date_requested:
            print(f"  Date: {response.date_requested}")
        else:
            print("  Date: Latest available")

        # Show top 5 stocks by comment count
        if response.data:
            print("\nTop 5 stocks by comment count:")
            sorted_stocks = sorted(
                response.data,
                key=lambda x: x.no_of_comments,
                reverse=True,
            )
            for stock in sorted_stocks[:5]:
                print(
                    f"  {stock.ticker:6} - {stock.no_of_comments:4} comments "
                    f"({stock.sentiment}, score: {stock.sentiment_score:.3f})"
                )

        # Save to JSON
        filepath = save_to_json(
            response,
            output_dir=parsed_args.output,
            filename=parsed_args.filename,
        )

        print(f"\n✓ Data saved to: {filepath}")
        logger.info("cli_completed_successfully", filepath=str(filepath))

        return 0

    except ValueError as e:
        logger.error("validation_error", error=str(e), exc_info=True)
        print(f"\n✗ Validation error: {e}", file=sys.stderr)
        return 1

    except TradestieAPIError as e:
        logger.error("api_error", error=str(e), exc_info=True)
        print(f"\n✗ API error: {e}", file=sys.stderr)
        return 1

    except StorageError as e:
        logger.error("storage_error", error=str(e), exc_info=True)
        print(f"\n✗ Storage error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.error("unexpected_error", error=str(e), exc_info=True)
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
