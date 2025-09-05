import logging
import sys
from enum import StrEnum

from pydantic import BaseModel

from src.common.settings import settings


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SETTINGS = "SETTINGS"


class LoggerSetup(BaseModel):
    name: str
    log_level: LogLevel


LOGGERS = [
    LoggerSetup(name="doclingtrials", log_level=LogLevel.SETTINGS),
    LoggerSetup(name="RapidOCR", log_level=LogLevel.WARNING),
]


def no_base_logger() -> None:
    logger = logging.getLogger()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])


def init_loggers() -> logging.Logger:
    no_base_logger()
    formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s %(filename)s line=%(lineno)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    for l in LOGGERS:
        logger = logging.getLogger(name=l.name)
        logger.addHandler(handler)
        logger.setLevel(settings.log_level if l.log_level == LogLevel.SETTINGS else l.log_level)
