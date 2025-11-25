# Exception Handling Comparison: Native vs Structlog vs Loguru

## Summary

All three implementations properly handle exceptions with **dedicated fields** (not dumped into message). However, they differ significantly in capabilities and ease of use.

---

## 1. Native Logging (stdlib) ✅

### Implementation
```python
# JSONFormatter handles exceptions
if record.exc_info:
    log_data["exception"] = self.formatException(record.exc_info)

if record.stack_info:
    log_data["stack_info"] = self.formatStack(record.stack_info)
```

### Usage
```python
logger.error("api_request_failed", error=str(e), exc_info=True)
```

### JSON Output
```json
{
  "timestamp": "2025-11-25 10:30:45",
  "level": "ERROR",
  "logger": "reddit_wsb_stocks.client",
  "message": "api_request_failed",
  "module": "client",
  "function": "get_stock_sentiment",
  "line": 203,
  "error": "Connection timeout",
  "exception": "Traceback (most recent call last):\n  File \"/app/client.py\", line 177, in get_stock_sentiment\n    response = client.get(self.base_url, params=params)\n  ...\nhttpx.ConnectTimeout: Connection timeout"
}
```

### Capabilities
- ✅ Dedicated `exception` field
- ✅ Dedicated `stack_info` field
- ✅ Full traceback as formatted string
- ❌ No structured exception data (exception is a string)
- ❌ No variable inspection
- ❌ No extended backtrace beyond catch point
- ❌ Manual `exc_info=True` required

---

## 2. Structlog (as currently implemented) ✅

### Implementation
```python
processors = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,  # Converts exc_info to string
]
```

### Usage
```python
logger.error("api_request_failed", error=str(e), exc_info=True)
```

### JSON Output (with format_exc_info)
```json
{
  "event": "api_request_failed",
  "error": "Connection timeout",
  "exception": "Traceback (most recent call last):\n  File \"/app/client.py\", line 177\n...",
  "level": "error",
  "logger": "reddit_wsb_stocks.client",
  "timestamp": "2025-11-25T10:30:45.123456Z"
}
```

### Capabilities
- ✅ Dedicated `exception` field
- ✅ Full traceback as formatted string
- ❌ No structured exception data (exception is a string)
- ❌ No variable inspection
- ❌ Manual `exc_info=True` required

### Structlog with `dict_tracebacks` (Enhanced) ⭐

```python
processors = [
    structlog.processors.dict_tracebacks,  # Instead of format_exc_info
    structlog.processors.JSONRenderer(),
]
```

### JSON Output (with dict_tracebacks)
```json
{
  "event": "api_request_failed",
  "error": "Connection timeout",
  "exception": {
    "exc_type": "httpx.ConnectTimeout",
    "exc_value": "Connection timeout",
    "syntax_error": null,
    "is_cause": false,
    "frames": [
      {
        "filename": "/app/client.py",
        "lineno": 177,
        "name": "get_stock_sentiment",
        "line": "response = client.get(self.base_url, params=params)",
        "locals": null
      }
    ]
  },
  "level": "error",
  "timestamp": "2025-11-25T10:30:45.123456Z"
}
```

### Enhanced Capabilities
- ✅ Dedicated `exception` field
- ✅ **Structured exception data** (parseable by log systems)
- ✅ Frame-by-frame breakdown
- ✅ Exception type, value separated
- ❌ No variable inspection (locals=null)
- ❌ Manual `exc_info=True` required

---

## 3. Loguru ⭐⭐⭐

### Implementation
```python
logger.add(
    log_dir / "reddit_wsb_stocks.log",
    level=log_level.upper(),
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
    serialize=True,  # JSON format
    backtrace=True,   # Extended traceback
    diagnose=False,   # Variable inspection (disable in prod)
)
```

### Usage
```python
# Option 1: Automatic exception capture
logger.exception("api_request_failed")

# Option 2: Manual with exc_info
logger.error("api_request_failed", error=str(e), exc_info=True)
```

### JSON Output (serialize=True)
```json
{
  "text": "2025-11-25 10:30:45.123 | ERROR | reddit_wsb_stocks.client:get_stock_sentiment:203 - api_request_failed\nTraceback (most recent call last):\n...",
  "record": {
    "elapsed": {"repr": "0:00:01.234567", "seconds": 1.234567},
    "exception": {
      "type": "httpx.ConnectTimeout",
      "value": "Connection timeout",
      "traceback": true
    },
    "extra": {
      "error": "Connection timeout"
    },
    "file": {"name": "client.py", "path": "/app/client.py"},
    "function": "get_stock_sentiment",
    "level": {"icon": "❌", "name": "ERROR", "no": 40},
    "line": 203,
    "message": "api_request_failed",
    "module": "client",
    "name": "reddit_wsb_stocks.client",
    "process": {"id": 1234, "name": "MainProcess"},
    "thread": {"id": 5678, "name": "MainThread"},
    "time": {"repr": "2025-11-25 10:30:45.123456+00:00", "timestamp": 1732532445.123456}
  }
}
```

### Capabilities (Basic)
- ✅ Dedicated exception data in `record.exception`
- ✅ Exception type, value, traceback flag
- ✅ Extremely rich context (process, thread, elapsed time)
- ✅ `.exception()` method captures exc_info automatically
- ❌ Exception as structured data but not fully detailed frames

### With `backtrace=True`
```python
logger.add("file.log", backtrace=True)
```
- ✅ **Extended backtrace** beyond the catching point
- ✅ Shows the **full call chain** that led to the error
- ✅ Includes frames from before the try/except block

### With `diagnose=True` (Development Only)
```python
logger.add("file.log", diagnose=True)  # ⚠️ NEVER in production
```
- ✅ **Variable values** in each frame
- ✅ Complete variable inspection for debugging
- ⚠️ **Security risk**: Can leak sensitive data (passwords, tokens, PII)

---

## Feature Comparison Matrix

| Feature | Native | Structlog (format_exc_info) | Structlog (dict_tracebacks) | Loguru |
|---|---|---|---|---|
| **Dedicated exception field** | ✅ | ✅ | ✅ | ✅ |
| **Dedicated stack_info field** | ✅ | ✅ | ✅ | ✅ |
| **Exception as string** | ✅ | ✅ | ❌ | Partial |
| **Structured exception (parseable)** | ❌ | ❌ | ✅ | ✅ |
| **Frame-by-frame breakdown** | ❌ | ❌ | ✅ | ✅ |
| **Extended backtrace** | ❌ | ❌ | ❌ | ✅ |
| **Variable inspection** | ❌ | ❌ | ❌ | ✅ (dev) |
| **Auto exc_info with .exception()** | ✅ | ✅ | ✅ | ✅ |
| **Rich context (process/thread)** | Partial | Partial | Partial | ✅ |
| **Setup complexity** | High | Moderate | Moderate | Low |

---

## Production Recommendations

### For Basic Exception Logging
**All three work fine** - they all put exceptions in dedicated fields, not in the message.

**Winner: Native or Loguru** (both work well, choose based on other factors)

### For Advanced Exception Debugging
**Winner: Loguru** with `backtrace=True`

**Why:**
- Extended backtrace shows the **full call chain**, not just from the catch point
- This is invaluable for tracking down root causes in production
- Example: If a function deep in your code raises an error, you see how it was called

**Example scenario:**
```python
def fetch_data():
    return api.get("/data")  # Fails here

def process():
    data = fetch_data()
    # ...

def main():
    process()

# With backtrace=True, you see:
# main() → process() → fetch_data() → api.get() → [error]
# Without it, you only see from the except block downward
```

### For Development/Debugging
**Winner: Loguru** with `diagnose=True`

**Why:**
- Variable inspection shows you the **exact state** when the error occurred
- No need to add print statements or debugger breakpoints

**Security Warning:**
```python
# Development
logger.add("dev.log", diagnose=True)  # Shows variable values

# Production
logger.add("prod.log", diagnose=False)  # Safe, no sensitive data
```

### For Log Analytics/APM Integration
**Winner: Structlog with dict_tracebacks**

**Why:**
- Fully structured exception data
- Easy to parse by log aggregation systems (ELK, Splunk, Datadog)
- Exception type/value as separate fields for filtering

---

## Real-World Example

### Scenario: API timeout in production

**What you log:**
```python
try:
    response = await client.get("/api/data")
except httpx.ConnectTimeout as e:
    logger.error("api_timeout", endpoint="/api/data", exc_info=True)
```

**What you get:**

#### Native Logging
```json
{
  "exception": "Traceback...\nhttpx.ConnectTimeout: timeout"
}
```
✅ Good: Exception is separate
❌ Limited: String format, hard to parse, no calling context

#### Structlog (dict_tracebacks)
```json
{
  "exception": {
    "exc_type": "httpx.ConnectTimeout",
    "frames": [...]
  }
}
```
✅ Good: Structured, parseable, filterable by exc_type
❌ Limited: No calling context beyond catch point

#### Loguru (backtrace=True)
```json
{
  "record": {
    "exception": {...},
    "elapsed": {"seconds": 1.234},
    "process": {"id": 1234},
    ...
  }
}
```
✅ Excellent: Full context, extended backtrace shows what led to the API call
✅ Rich metadata: Elapsed time, process info, thread info

---

## Final Recommendation

### Choose **Native Logging** if:
- You want zero dependencies
- Basic exception logging is sufficient
- You're willing to maintain the custom JSONFormatter

### Choose **Structlog** if:
- You need structured exceptions for APM tools
- You want maximum control over exception formatting
- Your team is already familiar with structlog

### Choose **Loguru** if:
- You want the best exception debugging experience
- `backtrace=True` for production root-cause analysis
- `diagnose=True` for development debugging
- You value simplicity (2 lines to set up vs custom formatters)

**For a backend handling tens of thousands of users:**
**Loguru wins** - The extended backtrace (`backtrace=True`) is invaluable for debugging production issues without the need for complex custom exception formatters.

---

## Sources

- [Structlog Exceptions Documentation](https://www.structlog.org/en/stable/exceptions.html)
- [Structlog dict_tracebacks GitHub](https://github.com/hynek/structlog/blob/main/docs/exceptions.md)
- [Loguru Exception Handling](https://loguru.readthedocs.io/en/stable/api/logger.html)
- [Loguru Complete Guide](https://betterstack.com/community/guides/logging/loguru/)
- [Loguru Overview](https://loguru.readthedocs.io/en/stable/overview.html)
