import logging
import sys


def setup_logger(name: str = "compliance_backend") -> logging.Logger:
    """
    Configures and returns a standard application logger.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    app_logger = logging.getLogger(name)
    if not app_logger.handlers:
        app_logger.setLevel(logging.INFO)
        app_logger.addHandler(handler)
        app_logger.propagate = False

    return app_logger


logger = setup_logger()
