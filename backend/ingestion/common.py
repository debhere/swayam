import sys
import json

import logging
import requests
import pymupdf

from typing import List, Dict, Tuple
from pathlib import Path

from bs4 import BeautifulSoup

from ingestion.helper import _get_refined_policy_name
from ingestion.helper import get_html_contents, get_document_type

from config import constants
from config.settings import appSettings

from utils.exception import CustomException
from utils.logger import setup_logging

from llama_cloud import LlamaCloud

setup_logging()
logger = logging.getLogger(__name__)

HOME_DIR: str = Path(__file__).parents[1]

def get_policy_urls(lic_web: str, product_url: str) -> List[str|None]:
    """Capture a urls of the policies for a given product. In case of insurance
    the product_url will act as a category url
    """
    try:
        soup: BeautifulSoup = get_html_contents(product_url)
        policy_urls: List[str|None] = []

        elements: List[str] = soup.find_all('td')

        logger.info("extracting the policy urls...")

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

        logger.info("Compiling the policy artefacts...")

        anchors: List[str] = policy_details.find_all('section', {'id': 'maincontent'})[0].find_all('a')
        links: List[str] = [anchor.get('href') for anchor in anchors]
        policy: str = policy_details.find_all('section', {'id': 'maincontent'})[0].find('h5').get_text()

        return links, policy
    except Exception as e:
        raise CustomException(e, sys)




def save_documents(product: str, base_url: str, document_mapping: Dict[str, str], 
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

            # print(documents)

            for doc_type, document in document_mapping.items():
                doc_url: str = f"{base_url}{document}"

                # doc_type_map: Dict = {0: 'policy_doc', 
                #                       1: 'cis',
                #                       2: 'sales_brochure'}


                policy_raw_loc: str = f"{INS_RAW_LOC}/{category}" if category is not None else INS_RAW_LOC
                Path(f"{policy_raw_loc}").mkdir(parents=True, exist_ok=True)

                policy: str = _get_refined_policy_name(policy=policy)

                doc_name: str = f"{policy.lower()}_{doc_type}"
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


def _get_destination_filepath(document_location: str) -> List[str]:
    path_list: List[str] = []

    for doc in Path(document_location).iterdir():
        if doc.is_dir():
            for d in Path(doc).iterdir():
                path_list.append(f"{doc.name}/{d.name}")
            continue
        path_list.append(doc.name)

    return path_list


def _get_parsing_configurations(document: str) -> Tuple[str, str]:
    tier_map: Dict[str, str] = {
        "cis": "agentic",
        "sales": "cost_effective",
        "policy": "cost_effective"
    }

    pages = pymupdf.open(document)
    total_pages = len(pages)

    pages_map: Dict[str, str] = {
        "cis": f"1-{total_pages}",
        "sales": f"2-{total_pages - 3}",
        "policy": f"1-{total_pages}"
    }

    doc_type = get_document_type(document)
    
    tier = tier_map[doc_type]
    target_pages = pages_map[doc_type]

    return tier, target_pages




def _create_metadata(product_category, document_name, product_subcategory=None):

    try:
        METADATA_DIR: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}/{constants.METADATA_DIR}"
        Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)

        doc_type_map: Dict[str] = {
            'cis': "CUSTOMER INFORMATION SHEET",
            'sales': "SALES BROCHURE",
            'policy': "POLICY DOCUMENT"
        }

        doc_type: str = get_document_type(document=document_name)
        std_doc_type: str = doc_type_map[doc_type]

        idx = document_name.find(f"_{doc_type}")
        policy_name = document_name[:idx].replace("_", " ")

        
        policy_name: str = document_name.replace("_cis", "").replace("_policy_doc", "").replace("_sales_brochure", "")
        policy_name = policy_name.replace(".pdf", "").replace("_", " ")

        file_metadata = {
            "policy_name": policy_name,
            "document_name": document_name,
            "document_type": std_doc_type,
            "product_category": product_category,
            "product_subcategory": product_subcategory,
            "product_status": "active"
        }

        filename = document_name.split('.')[0]
        filepath = Path(f"{METADATA_DIR}/{filename}.json")

        with open(filepath, "w") as f:
            json.dump(file_metadata, f, indent=2)

    except Exception as e:
        raise CustomException(e, sys)



def parse_pdf_to_markdown() -> None:
    """Converts the pdf files into their respoective mardown files. It loops through the folder and save the parsed document
    in the specific destination folder.

    Args:

    Returns:
    """
    try:

        logger.info("Parsing process getting initialized...")

        COMMON_PATH: str = f"{HOME_DIR}/{constants.PARENT_DATA_DIR}"
        SOURCE_BASE_DIR: str = f"{COMMON_PATH}/{constants.RAW_DATA_DIR}"
        DESTINATION_BASE_DIR: str = f"{COMMON_PATH}/{constants.PROCESSED_DATA_DIR}"

        client = LlamaCloud(api_key=appSettings.llama_cloud_api_key)

        for dir in Path(SOURCE_BASE_DIR).iterdir():
            product_category: str = dir.name

            SOURCE_DOC_DIR: str = f"{SOURCE_BASE_DIR}/{product_category}"
            PARSED_DOC_DIR: str = f"{DESTINATION_BASE_DIR}/{product_category}"

            logger.info(f"Compiling the source: {SOURCE_DOC_DIR} and destimation: {PARSED_DOC_DIR}")
            

            documents = _get_destination_filepath(dir)

            for document in documents:

                if document != document.split('/')[0]:
                    product_sub_category: str = document.split('/')[0]
                    DESTINATION_DIR: str = f"{PARSED_DOC_DIR}/{product_sub_category}"
                    SOURCE_DIR: str = f"{SOURCE_DOC_DIR}/{product_sub_category}"
                    document = document.split('/')[1]
                else:
                    DESTINATION_DIR: str = f"{PARSED_DOC_DIR}"
                    SOURCE_DIR: str = f"{SOURCE_DOC_DIR}"

                Path(DESTINATION_DIR).mkdir(parents=True, exist_ok=True)
                logger.info(f"parsing...{document}")

                filename = document.split('.')[0]

                try:
                    tier, target_pages = _get_parsing_configurations(f"{SOURCE_DIR}/{document}")
                    file = client.files.create(file=Path(f"{SOURCE_DIR}/{document}"), purpose="parse")
                    
                    result = client.parsing.parse(
                        file_id=file.id,
                        tier=tier,
                        version="latest",
                        expand=["markdown"],
                        page_ranges = {
                            "target_pages": target_pages
                        }
                    )

                    markdown_string = "\n\n".join(page.markdown for page in result.markdown.pages)

                    with open(Path(f"{DESTINATION_DIR}/{filename}.md"), "w", encoding="utf-8") as f:
                        f.write(markdown_string)

                    _create_metadata(product_category, document, product_sub_category)
                
                except Exception as e:
                    logger.info(f"Exception occured: {e}")
                    continue
    
    except Exception as e:
        raise CustomException(e, sys)

            
    