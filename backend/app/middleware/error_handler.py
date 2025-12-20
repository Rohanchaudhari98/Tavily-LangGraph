"""
Error handling middleware for FastAPI.

Provides centralized error handling and logging.
"""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

from app.utils.logging_config import log_error

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware.
    Catches all exceptions and returns appropriate responses.
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Flag slow requests for monitoring
        if process_time > 5000:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}ms"
            )
        
        return response
    
    except RequestValidationError as e:
        logger.warning(f"Validation error: {e.errors()}")
        log_error(e, {"path": str(request.url.path), "method": request.method})
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "detail": e.errors(),
                "path": str(request.url.path)
            }
        )
    
    except StarletteHTTPException as e:
        logger.warning(f"HTTP exception: {e.status_code} - {e.detail}")
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": "HTTP error",
                "detail": e.detail,
                "status_code": e.status_code
            }
        )
    
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        log_error(e, {
            "path": str(request.url.path),
            "method": request.method,
            "traceback": traceback.format_exc()
        })
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
                "error_id": id(e)
            }
        )