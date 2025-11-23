# Python Code Examples

## Error Logging

Logging with rich context

```python
try:
    response = api_client.fetch(url)
except httpx.HTTPError as e:
    logger.error(
        "api_fetch_failed",
        url=url,
        status_code=e.response.status_code if e.response else None,
        error_type=type(e).__name__,
        exc_info=True
    )
    raise
```
