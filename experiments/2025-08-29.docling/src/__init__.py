from logging import getLogger

from src.common.logging import init_loggers

init_loggers()
logger = getLogger("doclingtrials")
logger.debug("App initializing, importing modules.")
