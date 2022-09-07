import os
import sys
import logging
from functools import partial
from loguru import logger

JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False
LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'


class InterceptHandler(logging.Handler):

    def emit(self, record):
        if not (len(record.args) >= 2 and
                record.args[1] == "GET" and
                record.args[2] == "/ping"):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level,
                                                                   record.getMessage())


def setup_logging(log_level="DEBUG"):
    if log_level is None:
        log_level = "DEBUG"  # TODO for test

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]

    logging.root.setLevel(logging.getLevelName(log_level))

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # remove unwanted loggers
    logging.getLogger("urllib3").propagate = False
    logging.getLogger("pdfminer").propagate = False
    logging.getLogger("uamqp").propagate = False
    #logging.getLogger("azure").propagate = False
    logging.getLogger("aiohttp").propagate = False
    logging.getLogger("chardet").propagate = False

    # configure core logger of loguru
    logger.configure(handlers=[
        {
            "sink": sys.stdout,
            "format": LOG_FORMAT,
            "serialize": JSON_LOGS
        }
    ])


def check_and_add_name(envelope, prefix):
    if 'GET /ping HTTP/1.1' in envelope.data.baseData.message:
        return False
    else:
        envelope.tags['ai.operation.name'] = prefix
        return True


def cut_envelope_message(envelope):
    envelope.data.baseData.message = envelope.data.baseData.message[:30000]
    return True
