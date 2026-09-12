import sys
import requests
import logging

from typing import List, Dict
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

UNICODE_MAP = {
    "\u2013": "-", # en dash
    "\u2014": "-", # em dash
    "\u201c": '"', # left double quote
    "\u201d": '"', # right double quote
    "\u2018": "'", # left single quote
    "\u2019": "'"  # right single quote
}



def save_documents(product: str, base_url: str, documents: List[str], 
                   policy: str, category: str = None):
    try:
        RAW_DOC_LOC: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}/{constants.RAW_DATA_DIR}"
        Path(RAW_DOC_LOC).mkdir(parents=True, exist_ok=True)

        if product.lower() == 'insurance':
            INS_RAW_LOC: str = f"{RAW_DOC_LOC}/{product}"
            Path(INS_RAW_LOC).mkdir(parents=True, exist_ok=True)

            logging.info(f'Downloading {policy} artifacts...')

            print(documents)

            for idx, document in enumerate(documents):
                doc_url: str = f"{base_url}{document}"

                doc_type_map: Dict = {0: 'sales_brochure', 
                                      1: 'policy_doc',
                                      2: 'cis'}
                
                # if not document.isascii():
                #     doc_type_map: dict = {'0': 'sales'}
                # elif 'sales' in document.lower() or 'brochure' in document.lower():
                #     doc_type: str = "sales_brochure"
                # elif 'cis' in document.lower():
                #     doc_type: str = 'cis'
                # else:
                #     doc_type: str = 'policy_doc'



                policy_raw_loc: str = f"{INS_RAW_LOC}/{category}"
                Path(f"{policy_raw_loc}").mkdir(parents=True, exist_ok=True)

                # logger.info(f"Accessing {policy_raw_loc}...")

                for char, replacement in UNICODE_MAP.items():
                    policy = policy.replace(char, replacement)

                policy = policy.replace("LIC's ", "").replace(" ", "_").replace("-", "")
                policy = policy.replace("(", "").replace(")", "").replace(":", "_")
                policy = policy.replace("/", "_").replace("'s", "")

                doc_name: str = f"{policy.lower()}_{doc_type_map[idx]}"
                filepath = Path(f"{policy_raw_loc}/{doc_name}.pdf")

                if doc_name.startswith("female"):
                    print(f"{doc_name}: {filepath}")

                try:

                    with open(filepath, 'wb') as f:
                        f.write(requests.get(doc_url).content)
                except Exception as e:
                    print(f"Something happend: {e}")
                    logger.info(e)
                    logger.info(policy)
                    logger.info(doc_name)
                    continue

    except Exception as e:
        raise CustomException(e, sys)