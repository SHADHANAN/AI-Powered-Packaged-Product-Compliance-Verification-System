import logging
import re
import sys


def mask_sensitive_data(text: str) -> str:
    """
    Masks API keys, passwords, and sensitive credentials in log strings.
    """
    if not isinstance(text, str):
        return text
    # Mask API keys and tokens
    text = re.sub(r'(?i)(api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*["\']?([^"\'\s]{4})[^"\'\s]+([^"\'\s]{4})["\']?', r'\1: \2****\3', text)
    return text


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

