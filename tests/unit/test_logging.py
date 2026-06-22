import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_includes_request_id() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request complete",
        args=(),
        exc_info=None,
    )
    record.request_id = "request-123"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "request complete"
    assert payload["request_id"] == "request-123"
    assert payload["level"] == "INFO"

