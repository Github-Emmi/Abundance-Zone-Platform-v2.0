"""
Request ID Middleware
Adds unique request ID to each request for tracing
"""

import uuid
from typing import Callable
from fastapi import Request, Response


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """Add unique request ID to each request"""

    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Add to request state
    request.state.request_id = request_id

    # Process request
    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    return response
