"""fintool's logging module.

This module provides LoggingHelper, which works like a helper class
to create and configure logger objects. Basically, it is a wrapper of
std logging module.

"""

import logging
import sys


class Error(Exception):
    """Base error class for this module.
    """


class InvalidValueError(Exception):
    pass


# TODO: add file handler
# TODO: config logging from file
class LoggingHelper:

    LOG_LEVEL = "info"
    FORMATTER = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )

    @classmethod
    def set_log_level(cls, log_level):
        if log_level == 'debug':
            cls.LOG_LEVEL = logging.DEBUG
        elif log_level == 'info':
            cls.LOG_LEVEL = logging.INFO
        elif log_level == 'warning':
            cls.LOG_LEVEL = logging.WARNING
        elif log_level == 'error':
            cls.LOG_LEVEL = logging.ERROR
        elif log_level == 'critical':
            cls.LOG_LEVEL = logging.CRITICAL
        else:
            raise InvalidValueError(f'Unsupported log level {log_level}')

    @classmethod
    def get_console_handler(cls):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(cls.FORMATTER)
        return console_handler

    @classmethod
    def get_logger(cls, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(cls.LOG_LEVEL)
        logger.addHandler(cls.get_console_handler())
        logger.propagate = False
        return logger
