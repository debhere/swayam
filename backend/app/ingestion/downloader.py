import sys
import requests

from bs4 import BeautifulSoup

from pathlib import Path
from typing import List

from app.config import constants
from app.utils.exception import CustomException
from app.utils.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def get_contents(url: str) -> bytes:
    return requests.get(url).content

def get_html_contents(url: str) -> BeautifulSoup:
    contents: bytes = requests.get(url).content
    soup = BeautifulSoup(contents, 'html.parser')
    return soup

def save_documents(product: str, base_url: str, documents: List[str], 
                   policy: str, category: str = None):
    HOME_DIR: str = Path(__file__).parents[2]

    RAW_DOC_LOC: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}/{constants.RAW_DATA_DIR}"
    Path(RAW_DOC_LOC).mkdir(parents=True, exist_ok=True)

    if product.lower() == 'insurance':
        INS_RAW_LOC: str = f"{RAW_DOC_LOC}/{product}"
        Path(INS_RAW_LOC).mkdir(parents=True, exist_ok=True)

        for document in documents:
            doc_url: str = f"{base_url}{document}"

            policy_raw_loc: str = f"{INS_RAW_LOC}/{category}"
            Path(f"{policy_raw_loc}").mkdir(parents=True, exist_ok=True)

            filepath = Path(f"{policy_raw_loc}/{policy}.pdf")

            with open(filepath, 'wb') as f:
                f.write(requests.get(doc_url).content)



def download_insurance_docs(base_url: str, prd_str: str, lic_url: str):
    try:
        prd_url: str = f"{base_url}{prd_str}"
        ins_content: BeautifulSoup = get_html_contents(prd_url)

        elements: List[str] = ins_content.find_all('li', attrs={'class': 'selected'})
        # all_anchors: List[str] = [lst.find_all('a') for lst in element]

        category_urls, categories = [], []
        
        for element in elements:
            for anchor in element.find_all('a'):
                category_urls.append(anchor.get('href'))
                categories.append(anchor.get_text().lower().replace(' ', '-'))
            

        #urls for each insurance category
        # category_urls: List[str] = [l.get('href') for l in all_anchors]

        # capturing insurance category names
        # categories: List[str] = [l.get_text().lower().replace(' ', '-') for l in category_urls]

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
                    save_documents("insurance", constants.LIC_WEB, 
                                links, policy, categories[idx])

    except Exception as e:
        raise CustomException(e, sys)




def main():
    try:
        base_url: str = constants.LIC_BASE_URL
        lic: str = constants.LIC_WEB

        for product, var in constants.PRODUCT_CATEGORIES.items():
            # url: str = f"{base_url}{var}"
            if product == 'insurance':
                download_insurance_docs(base_url, var, lic)


    except Exception as e:
        raise CustomException(e, sys)
    


if __name__ == "__main__":
    main()