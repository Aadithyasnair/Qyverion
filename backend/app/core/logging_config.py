import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    """
    Configures application-wide logging with structured formats.
    Redirects standard output and uses appropriate levels.
    """
    log_format = (
        "[%(asctime)s] %(levelname)-8s %(name)s:%(filename)s:%(lineno)d - %(message)s"
    )
    
    # Determine log level based on DEBUG settings
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Set up basic configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Minimize noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("app")
    logger.info(f"Logging initialized in {'DEBUG' if settings.DEBUG else 'INFO'} mode.")
