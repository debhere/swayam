import sys
import logging
import requests

from typing import List, Dict, Tuple
from pathlib import Path

from bs4 import BeautifulSoup

from app.ingestion.helper import _get_refined_policy_name
from app.ingestion.helper import get_html_contents

from app.config import constants
from app.utils.exception import CustomException
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

HOME_DIR: str = Path(__file__).parents[2]

def get_policy_urls(lic_web: str, product_url: str) -> List[str|None]:
    """Capture a urls of the policies for a given product. In case of insurance
    the product_url will act as a category url
    """
    try:
        soup: BeautifulSoup = get_html_contents(product_url)
        policy_urls: List[str|None] = []

        elements: List[str] = soup.find_all('td')

        for element in elements:
            for anchor in element.find_all('a'):
                policy_urls.append(f"{lic_web}{anchor.get('href')}")

        return policy_urls
    except Exception as e:
        raise CustomException(e, sys)


def get_policy_details(policy_url: str) -> Tuple[List[str], str]:
    """Function to capture the document links and the policy names from the product url for
    each product

    Args:
        policy_url: str, The url for each product's policy. In case of insurance this is the url
        for each insurance category's policy.
    Returns:
        Tuple: Contains the document links in a list and policy name
    """
    try:
        policy_details: BeautifulSoup = get_html_contents(policy_url)

        anchors: List[str] = policy_details.find_all('section', {'id': 'maincontent'})[0].find_all('a')
        links: List[str] = [anchor.get('href') for anchor in anchors]
        policy: str = policy_details.find_all('section', {'id': 'maincontent'})[0].find('h5').get_text()

        return links, policy
    except Exception as e:
        raise CustomException(e, sys)




def save_documents(product: str, base_url: str, documents: List[str], 
                   policy: str, category: str = None):
    """This function is the common function across LIC products to download the corresponding
    LIC artefacts and save in pdf.
    
    Args:
        product: str, The invoking LIC product module ['insurance', 'pension', 'mip', 'ulp']
        base_url: str, Base URL for the invoking LIC product
        documents: List[str], A List object that contains the document links to be downloaded
        policy: str, The policy name of the product. Used to name the document pdf file.
        category: str. Only applicable for insurance, None for other products.

    Returns:
    """
    try:
        RAW_DOC_LOC: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}/{constants.RAW_DATA_DIR}"
        Path(RAW_DOC_LOC).mkdir(parents=True, exist_ok=True)

        if product.lower() in ['insurance', 'pension', 'mip', 'ulp']:
            INS_RAW_LOC: str = f"{RAW_DOC_LOC}/{product}"
            Path(INS_RAW_LOC).mkdir(parents=True, exist_ok=True)

            logging.info(f'Downloading {policy} artifacts...')

            print(documents)

            for idx, document in enumerate(documents):
                doc_url: str = f"{base_url}{document}"

                doc_type_map: Dict = {0: 'sales_brochure', 
                                      1: 'policy_doc',
                                      2: 'cis'}


                policy_raw_loc: str = f"{INS_RAW_LOC}/{category}" if category is not None else INS_RAW_LOC
                Path(f"{policy_raw_loc}").mkdir(parents=True, exist_ok=True)

                policy: str = _get_refined_policy_name(policy=policy)

                doc_name: str = f"{policy.lower()}_{doc_type_map[idx]}"
                filepath = Path(f"{policy_raw_loc}/{doc_name}.pdf")

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