import sys
import logging


from typing import List

from app.ingestion.common import save_documents, get_policy_urls
from app.ingestion.common import get_policy_details

from app.ingestion.helper import get_relevant_documents

from app.utils.exception import CustomException
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def download_other_product_docs(base_url: str, prd_str: str, lic_url: str, product: str):
    """Primary function to download the policy artefacts for different LIC products. LIC products
     - 'pension', 'ulp', 'mip' are leveraging this function

     Args:
        base_url: str, The base url of the product.
        prd_str: str, The relevant product string in the LIC website
        lic_url: str, LIC website.
        product: str, Product type
    """
    try:
        logger.info(f"Navigating to LIC's {product} module...")

        # Building the product url and getting the corresponding policy urls
        product_url: str = f"{base_url}{prd_str}"
        policy_urls: List[str] = get_policy_urls(lic_url, product_url)

        # Looping through the policy urls to fetch the document links and save in pdf.
        for url in policy_urls:
            links, policy = get_policy_details(url)

            links = get_relevant_documents(links)

            save_documents(product, lic_url, links, policy)
        logger.info(f"{product} documents are downloaded...")
    except Exception as e:
        raise CustomException(e, sys)