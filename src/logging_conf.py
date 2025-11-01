from __future__ import annotations

import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
"version": 1,
"disable_existing_loggers": False,
"formatters": {
"default": {
"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
},
},
"handlers": {
"console": {
"class": "logging.StreamHandler",
"formatter": "default",
},
},
"root": {
"handlers": ["console"],
"level": "INFO",
},
}

def configure_logging() -> None:
"""Configure structured logging for the application."""
dictConfig(LOGGING_CONFIG)
logging.getLogger(__name__).debug("Logging configured")

all = ["configure_logging", "LOGGING_CONFIG"]
