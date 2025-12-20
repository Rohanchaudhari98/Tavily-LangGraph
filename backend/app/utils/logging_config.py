"""
Logging configuration for the application.

Provides structured logging with file output and rotation.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / 'app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors and above)
    error_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / 'errors.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_format)
    root_logger.addHandler(error_file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured: level={log_level}, log_dir={log_dir}")


def log_request_response(request_data: dict, response_data: dict = None, duration_ms: float = None):
    """
    Log request and response data in structured format.
    
    Args:
        request_data: Request information (method, path, query_id, etc.)
        response_data: Response information (status_code, etc.)
        duration_ms: Request duration in milliseconds
    """
    logger = logging.getLogger("request_response")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "request": request_data,
    }
    
    if response_data:
        log_entry["response"] = response_data
    
    if duration_ms is not None:
        log_entry["duration_ms"] = duration_ms
    
    logger.info(json.dumps(log_entry))


def log_error(error: Exception, context: dict = None):
    """
    Log error with context information.
    
    Args:
        error: Exception object
        context: Additional context (query_id, user_id, etc.)
    """
    logger = logging.getLogger("errors")
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "error_traceback": None,  # Can add traceback if needed
    }
    
    if context:
        error_entry["context"] = context
    
    logger.error(json.dumps(error_entry))

