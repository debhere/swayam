import sys
import requests
import logging

from typing import List
from pathlib import Path
from bs4 import BeautifulSoup

from app.config import constants
from app.utils.exception import CustomException
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

HOME_DIR: str = Path(__file__).parents[2]

def get_contents(url: str) -> bytes:
    return requests.get(url).content

def get_html_contents(url: str) -> BeautifulSoup:
    contents: bytes = requests.get(url).content
    soup = BeautifulSoup(contents, 'html.parser')
    return soup



def save_documents(product: str, base_url: str, documents: List[str], 
                   policy: str, category: str = None):

    try:

        RAW_DOC_LOC: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}/{constants.RAW_DATA_DIR}"
        Path(RAW_DOC_LOC).mkdir(parents=True, exist_ok=True)

        if product.lower() == 'insurance':
            INS_RAW_LOC: str = f"{RAW_DOC_LOC}/{product}"
            Path(INS_RAW_LOC).mkdir(parents=True, exist_ok=True)

            logging.info('Downloading insurance artifacts...')

            for document in documents:
                doc_url: str = f"{base_url}{document}"

                policy_raw_loc: str = f"{INS_RAW_LOC}/{category}"
                Path(f"{policy_raw_loc}").mkdir(parents=True, exist_ok=True)

                logger.info(f"Accessing {policy_raw_loc}...")

                filepath = Path(f"{policy_raw_loc}/{policy}.pdf")

                try:

                    with open(filepath, 'wb') as f:
                        f.write(requests.get(doc_url).content)
                except Exception as e:
                    print(f"Something happend: {e}")
                    logger.info(e)
                    logger.info(policy)
                    continue

    except Exception as e:
        raise CustomException(e, sys)