import sys
import logging


from typing import List
from bs4 import BeautifulSoup

from app.ingestion.common import save_documents, get_policy_urls, get_policy_details
from app.ingestion.helper import get_html_contents, get_relevant_documents

from app.utils.exception import CustomException
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def download_insurance_docs(base_url: str, prd_str: str, lic_url: str):
    """Primary function to download the insurance policy artefacts for different LIC products. 

     Args:
        base_url: str, The base url of the product.
        prd_str: str, The relevant product string in the LIC website
        lic_url: str, LIC website.
    """
    try:
        logger.info("Navigating to LIC's insurance module...")
        
        # Building the product url
        prd_url: str = f"{base_url}{prd_str}"
        ins_content: BeautifulSoup = get_html_contents(prd_url)

        # Gathering the web elements that contains the insurance categories
        elements: List[str] = ins_content.find_all('li', attrs={'class': 'selected'})

        category_urls, categories = [], []
        
        # Looping through the captured web elements to capture the urls for each category
        for element in elements:
            for anchor in element.find_all('a'):
                category_urls.append(anchor.get('href'))
                categories.append(anchor.get_text().lower().replace(' ', '-'))
            
        logger.info("Compiling the insurance categories...")

        # navigating to each insurance category
        for idx, cat_url in enumerate(category_urls):
            policy_urls: List[str] = get_policy_urls(lic_url, cat_url) # getting the policy urls for each category

            # Capturing the documents for each policy for each category
            for url in policy_urls:
                links, policy = get_policy_details(url)
                links = get_relevant_documents(links)
                save_documents("insurance", lic_url, links, policy, categories[idx]) # Saving documents

        logger.info("Insurance documents are downloaded...")
    except Exception as e:
        raise CustomException(e, sys)