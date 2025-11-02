"""
Logging configuration for MCP Flight Search.
"""
import logging
import os
import sys

def setup_logging():
    # Respect MCP_LOG_LEVEL environment variable, default to CRITICAL
    # For MCP stdio mode, we must not output anything to stdout except JSON
    log_level_name = os.environ.get("MCP_LOG_LEVEL", "CRITICAL").upper()
    log_level = getattr(logging, log_level_name, logging.CRITICAL)

    # Send all logs to stderr to avoid breaking MCP JSON protocol on stdout
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "| %(levelname)-8s | %(name)s | %(message)s"
    ))

    """Configure and set up logging for the application."""
    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        force=True  # Override uvicorn & third-party loggers
    )

    logger = logging.getLogger("flight_search")
    # Suppress all third-party loggers to avoid stdout pollution
    logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)

    return logger

# Create the logger instance for import by other modules
logger = setup_logging() 
