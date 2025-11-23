# Reddit WSB Stocks

A Python package for retrieving stock sentiment data from Reddit's WallStreetBets (WSB) community via the Tradestie API.

## Features

- 🚀 **Simple API**: Easy-to-use client for fetching WSB stock sentiment data
- ✅ **Type-Safe**: Full type annotations with Pydantic validation
- 📊 **Data Validation**: Automatic validation of API responses
- 💾 **JSON Storage**: Save data to JSON files with automatic timestamping
- 🎨 **Structured Logging**: Beautiful, structured logs with `loguru`
- 🧪 **Well Tested**: 87% test coverage with pytest
- 🔧 **CLI Interface**: Command-line tool for quick data fetching
- ⚡ **Async Support**: Both sync and async API methods

## Installation

### Using `uv` (Recommended)

```bash
uv add reddit-wsb-stocks
```

### Using `pip`

```bash
pip install reddit-wsb-stocks
```

## Quick Start

### CLI Usage

Fetch the latest WSB stock sentiment data:

```bash
# Get latest data
python -m reddit_wsb_stocks

# Get data for a specific date
python -m reddit_wsb_stocks --date 11-02-2025

# Specify output directory
python -m reddit_wsb_stocks --output data/stocks

# Custom filename
python -m reddit_wsb_stocks --filename my_data.json

# Adjust log level
python -m reddit_wsb_stocks --log-level DEBUG
```

### Python API

#### Basic Usage

```python
from reddit_wsb_stocks import TradestieClient, save_to_json

# Create client
client = TradestieClient()

# Fetch latest data
response = client.get_stock_sentiment()

# Save to JSON
filepath = save_to_json(response, output_dir="data")

print(f"Saved {len(response.data)} stocks to {filepath}")

# Access individual stocks
for stock in response.data:
    print(f"{stock.ticker}: {stock.sentiment} ({stock.sentiment_score:.2f})")
```

#### Fetch Historical Data

```python
from reddit_wsb_stocks import TradestieClient

client = TradestieClient()

# Get data for a specific date (MM-DD-YYYY format)
response = client.get_stock_sentiment(date="11-02-2025")
```

#### Async Usage

```python
import asyncio
from reddit_wsb_stocks import TradestieClient

async def fetch_data():
    async with TradestieClient() as client:
        response = await client.aget_stock_sentiment()
        print(f"Fetched {len(response.data)} stocks")

asyncio.run(fetch_data())
```

#### Load Saved Data

```python
from reddit_wsb_stocks import load_from_json

# Load previously saved data
response = load_from_json("data/wsb_stocks_20251123_120000.json")

for stock in response.data:
    print(f"{stock.ticker}: {stock.no_of_comments} comments")
```

## API Response Format

The API returns data in the following structure:

```json
{
    "fetched_at": "2025-11-23T12:00:00",
    "date_requested": "11-02-2025",
    "count": 3,
    "stocks": [
        {
            "ticker": "GME",
            "sentiment": "Bullish",
            "sentiment_score": 0.13,
            "no_of_comments": 179
        },
        {
            "ticker": "AMC",
            "sentiment": "Bearish",
            "sentiment_score": -0.159,
            "no_of_comments": 37
        }
    ]
}
```

### Data Fields

- **ticker**: Stock ticker symbol (e.g., "GME", "AMC")
- **sentiment**: Overall sentiment classification ("Bullish", "Bearish", or "Neutral")
- **sentiment_score**: Numerical sentiment score (-1.0 to 1.0)
- **no_of_comments**: Number of Reddit comments mentioning this ticker

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/reddit-wsb-stocks.git
cd reddit-wsb-stocks

# Install with dev dependencies
uv sync --dev

# Install pre-commit hooks
uv run prek install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check --fix

# Type checking
uv run pyrefly check

# Check docstring coverage
uv run interrogate src
```

### Pre-commit Hooks

The project uses `prek` for pre-commit hooks that automatically:
- Format code with `ruff`
- Lint code with `ruff`
- Type check with `pyrefly`
- Check docstring coverage with `interrogate`
- Run tests with `pytest`

## Architecture

The package follows best practices for production Python code:

- **SOLID Principles**: Clean, maintainable code structure
- **Type Safety**: Full type annotations checked by `pyrefly`
- **Data Validation**: Pydantic models for robust validation
- **Structured Logging**: Rich logging with `structlog`
- **Comprehensive Testing**: 87% code coverage
- **Documentation**: 100% docstring coverage

### Project Structure

```
reddit-wsb-stocks/
├── src/
│   └── reddit_wsb_stocks/
│       ├── __init__.py         # Public API exports
│       ├── __main__.py         # CLI entry point
│       ├── cli.py              # Command-line interface
│       ├── client.py           # API client
│       ├── models.py           # Pydantic models
│       ├── storage.py          # JSON storage
│       └── logging_config.py   # Logging setup
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## API Reference

### TradestieClient

Main client for interacting with the Tradestie API.

#### Methods

- `get_stock_sentiment(date: str | None = None) -> APIResponse`
  - Fetch stock sentiment data (synchronous)
  - Returns latest data if `date` is None

- `aget_stock_sentiment(date: str | None = None) -> APIResponse`
  - Fetch stock sentiment data (asynchronous)

- `close()` - Close the HTTP client
- `aclose()` - Close the async HTTP client

### Storage Functions

- `save_to_json(data, output_dir="data", filename=None, pretty=True) -> Path`
  - Save data to JSON file

- `load_from_json(filepath) -> APIResponse`
  - Load data from JSON file

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Credits

- Data provided by [Tradestie API](https://tradestie.com/)
- Built with Python, httpx, Pydantic, and structlog
