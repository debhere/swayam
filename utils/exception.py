import sys
from .logger import logging

def exception_details(error: Exception, error_details: sys) -> str:
    _, _, tb = error_details.exc_info()
    filename: str = tb.tb_frame.f_code.co_filename
    error_message: str = f"Error occured in {filename}, line number {tb.tb_lineno}: {error}"
    logging.info(error_message)
    return error_message

class CustomException(Exception):
    def __init__(self, error_message: Exception, error_details: sys):
        super().__init__(str(error_message))
        self.error_message = exception_details(error_message, error_details)
    def __str__(self):
        return self.error_message