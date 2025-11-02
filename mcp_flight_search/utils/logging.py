"""
Logging configuration for MCP Flight Search.
"""
import logging
import os
from rich.logging import RichHandler

def setup_logging():
    # Respect MCP_LOG_LEVEL environment variable, default to ERROR
    # Otherwise we get all sorts of horrible parsing errors for non-JSON messages
    log_level_name = os.environ.get("MCP_LOG_LEVEL", "ERROR").upper()
    log_level = getattr(logging, log_level_name, logging.ERROR)


    """Configure and set up logging for the application."""
    logging.basicConfig(
        level=log_level,
        format="| %(levelname)-8s | %(name)s | %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(rich_tracebacks=True)],
        force=True  # This is the fix that overrides uvicorn & third-party loggers
    )

    logger = logging.getLogger("flight_search")
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger

# Create the logger instance for import by other modules
logger = setup_logging() 
