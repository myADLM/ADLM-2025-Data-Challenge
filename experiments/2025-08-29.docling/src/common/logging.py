import logging
import sys

from src.common.settings import settings


def no_base_logger() -> None:
    logger = logging.getLogger()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])


def init_loggers(names: list[str]) -> logging.Logger:
    no_base_logger()
    formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s %(filename)s line=%(lineno)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    for name in names:
        logger = logging.getLogger(name=name)
        logger.addHandler(handler)
        logger.setLevel(settings().LOG_LEVEL)
