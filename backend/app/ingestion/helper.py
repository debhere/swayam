import requests
from typing import List, Dict
from bs4 import BeautifulSoup


_UNICODE_MAP = {
    "\u2013": "-", # en dash
    "\u2014": "-", # em dash
    "\u201c": '"', # left double quote
    "\u201d": '"', # right double quote
    "\u2018": "'", # left single quote
    "\u2019": "'"  # right single quote
}

# def get_contents(url: str) -> bytes:
#     return requests.get(url).content

def get_html_contents(url: str) -> BeautifulSoup:
    """Returns a soup of object for a passing web url
    """
    print(url)
    contents: bytes = requests.get(url, timeout=30).content
    soup = BeautifulSoup(contents, 'html.parser')
    return soup


def get_relevant_documents(documents: List[str], start: int=-3, end: int=None) -> List[str]:
    """Returns a slice of the documents with the given stanrt and end indices. By default the last
    three elements are returned.
    """
    return documents[start:] if end is None else documents[start:end]

def get_document_map(documents: List[str]) -> Dict[str, str]:
    document_map: Dict[str, str] = {}

    for document in documents:
        if document.lower().find("policy") != -1:
            document_map['policy_doc'] = document
        elif document.lower().find("cis") != -1:
            document_map['cis'] = document
        elif document.lower().find("sales") != -1:
            document_map['sales_brochure'] = document
        elif 'sales_brochure' not in document_map.keys():
            document_map['sales_brochure'] = document
        elif 'policy_doc' not in document_map.keys():
            document_map['policy_doc'] = document
        elif 'cis' not in document_map.keys():
            document_map['cis'] = document

    if len(documents) == 3 and len(document_map) == 0:
        document_map = {'policy_doc': documents[0], 'cis': documents[1], 'sales_brochure': documents[2]}
    if len(documents) == 2 and len(document_map) == 0:
        document_map = {'policy_doc': documents[0], 'sales_brochure': documents[1]}

    return document_map


def _get_refined_policy_name(policy: str) -> str:
    """Replaces the unicode characters and other unwanted characters from the passing string
    and returns the refined string.
    """
    for char, replacement in _UNICODE_MAP.items():
        policy = policy.replace(char, replacement)
    
        policy = policy.replace("LIC's ", "").replace(" ", "_").replace("-", "")
        policy = policy.replace("(", "").replace(")", "").replace(":", "_")
        policy = policy.replace("/", "_").replace("'s", "")
        return policy


