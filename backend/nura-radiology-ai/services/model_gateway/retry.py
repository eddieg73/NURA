"""Retry with structured fallback (spec: JSON mode can return empty content -> validate, retry, fallback)."""
import time, logging

logger = logging.getLogger("nura.gateway.retry")


def with_retry(fn, attempts=3, base_delay=0.6, validator=None):
    """Call fn() up to `attempts`. If validator(result) is falsy, retry with backoff.
    On final failure, raises RuntimeError (caller decides fallback route)."""
    last = None
    for i in range(attempts):
        try:
            result = fn()
            if validator is None or validator(result):
                return result
            last = RuntimeError("result did not validate")
            logger.warning("invalid result attempt %d: %s", i + 1, last)
        except Exception as e:
            last = e
            logger.warning("retry %d failed: %s", i + 1, e)
        time.sleep(base_delay * (2 ** i))
    raise last if last else RuntimeError("retry exhausted")


def validate_schema(output, model):
    """Try to coerce a raw dict into the Pydantic schema; return None on any mismatch (for retry)."""
    try:
        return model.model_validate(output)
    except Exception:
        return None
