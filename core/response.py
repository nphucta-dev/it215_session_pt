from datetime import datetime, timezone
from typing import Any


def build_response(
    status_code: int,
    data: Any = None,
    message: str = "OK",
    path: str = "",
    error: Any = None,
) -> dict:
    return {
        "statusCode": status_code,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
        "error": error,
    }
