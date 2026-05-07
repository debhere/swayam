import sys
import requests

from typing import Dict
from pathlib import Path
from bs4 import BeautifulSoup

from utils import config
from utils.logger import logging
from utils.exception import CustomException


def getContent(url: str) -> bytes|None:
    """This is a simple function that accepts an url as an argument and returns the web content
    in bytes stream.

    Args:
        url: str, url of the website.

    Returns:
        bytes: response.content, The content of the response ofject from the request. get(url) call.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception
    return response.content


def getSoup(url: str) -> BeautifulSoup:
    """This is a simple function that returns a BeautifulSoup object every time invoked. The function
    takes an url of a website as an argument. It invokes the getContent() function to get the content
    of the given website. The parsed web content in the BeautifulSoup object is then returned.

    Args:
        url: str, url of a website.

    Returns:
        BeautifulSoup: BeautifulSoup object
    """
    content = getContent(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        return soup


def getPagesForInsurancePlans(soup: BeautifulSoup) -> Dict:
    elements = [elem.find('a').find_next('ul', class_='child-menu') for elem in soup.select('li.has-sub')]
    elems = set(elem.find_next('ul', class_="child-menu") for elem in elements if "Insurance" in elem.find_next('li').find_next('a')['title']\
         and "Plan" in elem.find_next('li').find_next('a')['title'])
    
    policy_map = {}

    for elem in elems:
        links = elem.find_all('a')
        for link in links:
            policy_map[link['title'].strip().replace(' ', '_')] = link['href']
            
    return policy_map


def getInsurancePlanLinks(policyPage: Dict) -> Dict:
    policy_links = {}
    for p, l in policyPage.items():
        soup = getSoup(l)
        policy_links[p] = {link.text.strip().replace("LIC's ", '').replace("LIC’s ", '').replace(' ', '_').replace('(', '') \
                           .replace(')', '').replace(':', ''): link['href'] \
                           for link in soup.find_all('a') if 'LIC' in link.text and 'https' not in link['href'] and 'guest' in link['href']}
    return policy_links


def getPolicyLinksPerPlan(base: str, planLinks: Dict) -> Dict:
    pdfLinks = {}
    for plan, links in planLinks.items():
        policyMap = {}
        for policy, link in links.items():
            soup = getSoup(f"{base}/{link}")
            pdf = [link['href'] for link in soup.find_all('a') if "Policy Document" in link.text][0]
            pdf = pdf[: pdf.index('pdf') + 3]
            policyMap[policy] = pdf
        pdfLinks[plan] = policyMap
    return pdfLinks



def downloadPolicyDocuments(url: str, pdfs: Dict, folder: str):
    for plan, policyPdfs in pdfs.items():
        for policy, pdf in policyPdfs.items():
            file_location = Path(f"{folder}/{plan.lower()}")
            if not file_location.is_dir():
                file_location.mkdir(parents=True, exist_ok=True)
            with open(f"{file_location}/{policy.lower()}.pdf", 'wb') as f:
                pdf_link = f"{url}/{pdf}"
                f.write(getContent(pdf_link))



def run(url: str, location: str) -> str:
    soup = getSoup(url)
    plan_pages = getPagesForInsurancePlans(soup)
    plan_links = getInsurancePlanLinks(plan_pages)
    # return plan_links
    planPdfs = getPolicyLinksPerPlan(url, plan_links)
    downloadPolicyDocuments(url, planPdfs, location)
    return "OK"


if __name__ == "__main__":
    try:
        url: str = config.URL
        policies: str = config.RAW_DATA_FOLDER
        logging.info("Intiate scraping")
        run(url, policies)

    except Exception as e:
        raise CustomException(e, sys)



