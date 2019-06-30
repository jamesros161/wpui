"""Constructs Application logger
"""
import logging
import sys
import getpass
from settings import Settings
S = Settings()
class Log(object):
    """Logging class for application logger
    """
    def __init__(self):
        log_format = S.logging['format']
        log_name = S.logging['name']
        if getpass.getuser() == 'root':
            logpath = '/root/' + log_name
        else:
            logpath = '/home/' + getpass.getuser() + '/' + log_name
        logging_level = getattr(logging, S.logging['level'])
        logging.basicConfig(format=log_format,
                            filename=logpath,
                            filemode='a',
                            level=logging_level,
                            datefmt=S.logging['datefmt'])
        logging.addLevelName(10, "**DEBUG**")
        logging.addLevelName(20, "**INFO** ")
        logging.addLevelName(30, "*WARNING*")
        logging.addLevelName(40, "**ERROR**")
        logging.addLevelName(50, "**FATAL**")

        logger = logging.getLogger(__name__)
        handler = logging.FileHandler(filename=logpath, mode='a')
        logger.addHandler(handler)

        self.logger = logger
        self.info = logger.info
        self.debug = logger.debug
        self.warning = logger.warning

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handles all otherwise unhandled exceptions, sending them to the Log

        Arguments:
            exc_type {[str]} -- [Type of exception]
            exc_value {[str]} -- [Value of exception]
            exc_traceback {[str]} -- [Exception traceback]
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
