import sys
import logging

from utils.exception import CustomException
from ingestion.common import parse_pdf_to_markdown
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    try:
        parse_pdf_to_markdown()
        print("All documents are parsed successfuly into markdown files...!!")
        logging.info("parsing is completed...")
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    main()