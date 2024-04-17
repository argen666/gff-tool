import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GFF")
logger.setLevel(logging.INFO)


def enable_debug_logging():
    logger.setLevel(logging.DEBUG)
