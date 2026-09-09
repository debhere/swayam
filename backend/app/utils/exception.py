import sys
import logging
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def exception_details(error, error_details: sys):
    _, _, exc_tb = error_details.exc_info()
    filename: str = exc_tb.tb_frame.f_code.co_filename
    log_message: str = f"Error occured in {filename}, line number {exc_tb.tb_lineno}: {str(error)}"
    logger.info(log_message)


class CustomException(Exception):
    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)
        self.error_message = exception_details(error_message, error_details=error_details)

    def __str__(self):
        return self.error_message
