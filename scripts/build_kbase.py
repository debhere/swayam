import sys
import os
import json

import pdfplumber

from typing import Dict, List
from pathlib import Path

from utils import config
from utils.exception import CustomException
from utils.logger import logging


UNICODE_MAP = {
    "\u2013": "-", # en dash
    "\u2014": "-", # em dash
    "\u201c": '"', # left double quote
    "\u201d": '"', # right double quote
    "\u2018": "'", # left single quote
    "\u2019": "'"  # right single quote
}

def is_covered_by_object(page, threshold=0.85) -> bool:
    """This function calculates the coverage percentage if a table or a rectangular object exists in a pdf
    page. Then returns True if the coverage percentage is greater then the thershold.

    First, the overall area of the page is calculated. If table or rectangulat objects exists then the overall
    area of those objects are calculated. The percentage calculation is simple.

    Args:
        page: pdf page.
        thershold: 0.85.

    Returns:
        True if coverage >= 0.85 else False

    """
    try:
        page_area = page.width * page.height
        object_area = 0
        tables = page.find_tables()
        
        for table in tables:
            x0, top, x1, bottom = table.bbox
            object_area += (x1 - x0) +(bottom - top)
        
        for rect in page.rects:
            object_area += (rect['x1'] - rect['x0']) * (rect['y1'] - rect['y0']) * (rect['bottom'] - rect['top'])
            
        coverage_ratio = object_area / page_area
        return coverage_ratio >= threshold
    
    except Exception as e:
        raise CustomException(e, sys)


def extract_text_from_file(filepath: str) -> List[dict]:
    """This is the most important function which extracts the texts page by page from the pdf file and 
    accordingly extracts the required content for each page.

    While extracting text, there are certain cleaning steps which are incorporated:
        i) trailing spaces are removed.
        ii) footer is removed.
        iii) lines with Blank fields are removed.
        iv) certain characters are replaced with it's unicode equivalent.

    For each page, the schema would contain:
        i) page number
        ii) page type
        iii) cleaned text

    Args:
        filepath: str, the path of the pdf file.
    
    Returns:
        text_by_page: List[Dict], a list of dictionary containing the cleaned content for each page.

    """

    try:
        text_by_page = []
        with pdfplumber.open(filepath) as pdf:
            for pageno, page in enumerate(pdf.pages):            
                original_text = page.extract_text()
                if original_text and original_text.strip():
                    if original_text.rfind('\n') == -1 and len(page.extract_text_lines()) == 1:
                        cleaned_text = original_text.replace(page.extract_text_lines()[-1]['text'], '')
                    else:
                        cleaned_text = original_text[:original_text.rindex('\n')]
                        for line in cleaned_text.split('\n'):
                            if line.strip()[-1] == ':' or line.strip() == '':
                                cleaned_text = cleaned_text.replace(f"{line}\n", '')
                                
                    if cleaned_text == "":
                        continue
                        
                    for char, replacement in UNICODE_MAP.items():
                        cleaned_text = cleaned_text.replace(char, replacement)
                    
                    page_type = 'form' if is_covered_by_object(page) else 'content'
                    if page_type == 'content' and ('Annexure' in cleaned_text[:50] or 'Schedule' in cleaned_text[:50]):
                        page_type = 'annexure'
                    elif page_type == 'content' and len(cleaned_text) <=50:
                        page_type = 'low_content'
                        
                    text_by_page.append({
                        "page": pageno + 1,
                        "page_type": page_type,
                        "text": cleaned_text.strip()
                    })
        return text_by_page
    
    except Exception as e:
        raise CustomException(e, sys)



def create_json_files(documents: List[Dict], destination: str) -> None:
    """The function creates json files for each corresponding pdf.

    The function gets the documents i.e., json content for each pdf file in a list of dictionary and then
    creates the corresponding json files in the given folder.

    Args:
        documents: List[Dict], list of documents.
        folder: str, base folder for json files to be stored.

    Returns: None
    """
    try:
        for document in documents:
            json_destination = Path(f"{destination}/{document['category']}")
            if not json_destination.is_dir():
                json_destination.mkdir(parents=True, exist_ok=True)
            with open(f"{json_destination}/{document['policy_name']}.json", "w") as file:
                json.dump(document, file, indent=2)
    except Exception as e:
        raise CustomException(e, sys)


def standardize_policy_files(source: str) -> List[dict]:
    """This function creates a list of all documents consisting the page contents for each pdf files
    along with their metadata as applicable. Category can be mapped as per the parent folder name of the 
    insurance policy pdfs and exact policy name is equal to the filename.

    Args:
        source: str, the source folder of the pdf files.

    Returns:
        all_docs: List[Dict], list of dictionary containing contents for each pdf file.

    """
    try:

        all_docs = []
        dirs = os.listdir(source)
        for category in dirs:
            path = Path(f"{source}/{category}")
            files = [file for file in path.iterdir() if file.is_file()]
            for file in files:
                if file.suffix != ".pdf":
                    continue
                file_content = extract_text_from_file(file)
                all_docs.append({
                    "policy_name": file.name.replace(".pdf", ""),
                    "category": category,
                    "source_path": str(path),
                    "pages": file_content
                })
        return all_docs
    
    except Exception as e:
        raise CustomException(e, sys)


def run(source: str, destination: str) -> str:
    """The controller function to create the json files into knwoledge-base for each policy document
    in the raw data.

    Args:
        source: str, the source folder for the raw files.
        destination: str, the destination folder for the json files to be stored.

    Returns:
        OK: str
    """
    try:
        logging.info("Raw data being compiled into standardized format...")
        documents: List[str] = standardize_policy_files(source=source)

        logging.info(f"Standardized data format is being utilized to create json files for knwoledge-base...")
        create_json_files(documents=documents, destination=destination)
        return "OK"
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        raw: str = config.RAW_DATA_FOLDER
        kb: str = config.KNOWLEDGE_BASE

        logging.info("Initiating knowledge-base creation from raw data...")
        run(raw, kb)
        logging.info("knowledge-base is successfully created...")
        print("knowledge-base is built successfully...")
    except Exception as e:
        raise CustomException(e, sys)


