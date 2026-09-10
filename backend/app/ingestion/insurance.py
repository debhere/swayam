import sys
import logging
import string

from typing import List
from bs4 import BeautifulSoup

from app.ingestion.helper import save_documents
from app.ingestion.helper import get_contents
from app.ingestion.helper import get_html_contents

from app.utils.exception import CustomException
from app.utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def download_insurance_docs(base_url: str, prd_str: str, lic_url: str):
    try:
        logger.info("Navigating to LIC's insurance product module...")
        
        prd_url: str = f"{base_url}{prd_str}"
        ins_content: BeautifulSoup = get_html_contents(prd_url)

        elements: List[str] = ins_content.find_all('li', attrs={'class': 'selected'})
        # all_anchors: List[str] = [lst.find_all('a') for lst in element]

        category_urls, categories = [], []
        
        for element in elements:
            for anchor in element.find_all('a'):
                category_urls.append(anchor.get('href'))
                categories.append(anchor.get_text().lower().replace(' ', '-'))
            
        logger.info("Compiling the insurance categories...")

        # navigating to each insurance category 
        for idx, cat_url in enumerate(category_urls):
            cat_content: BeautifulSoup = get_html_contents(cat_url)
            policy_rows: List[str] = cat_content.find_all('td')

            for row in policy_rows:
                for policy_link in row.find_all('a'):
                    policy_url: str = f"{lic_url}{policy_link.get('href')}"

                    print(policy_url)

                    policy_details: BeautifulSoup = get_html_contents(policy_url)

                    anchors: List[str] = policy_details.find_all('section', {'id': 'maincontent'})[0].find_all('a')
                    links: List[str] = [anchor.get('href') for anchor in anchors]
                    policy: str = policy_details.find_all('section', {'id': 'maincontent'})[0].find('h5').get_text()

                        
                    save_documents("insurance", lic_url, 
                                links, policy, categories[idx])

    except Exception as e:
        raise CustomException(e, sys)