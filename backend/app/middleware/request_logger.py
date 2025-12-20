"""
Request logging middleware.

Logs all incoming requests and responses for auditing and debugging.
"""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging_config import log_request_response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    # Middleware to log all HTTP requests and responses
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Grab request details
        request_data = {
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Pull out query_id if it's in the path or query params
        if "query_id" in request.path_params:
            request_data["query_id"] = request.path_params["query_id"]
        if "query_id" in request.query_params:
            request_data["query_id"] = request.query_params["query_id"]
        
        # Process the request
        response = await call_next(request)
        
        # Calculate how long it took
        duration_ms = (time.time() - start_time) * 1000
        
        # Get response details
        response_data = {
            "status_code": response.status_code,
        }
        
        # Log structured data for monitoring
        log_request_response(
            request_data=request_data,
            response_data=response_data,
            duration_ms=duration_ms
        )
        
        # Also log to console for easy viewing
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration_ms:.2f}ms"
        )
        
        return response