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
    """LIC has different categories for it's insurance products. There are multiple plans for each category. Each
    product has a dedicated url as well. This function extracts the html page link for each of the insurance plans 
    and maps it in a python dictionary.

    At first, all the links ('a' in html) are extracted into 'elements' through a list comprehension where there is a 
    sub list ('li.has-sub'). This now contains the web page url for all products.
    
    'elems' is the list where it filters out other html pages and only keeps the plans for the insurance
    products.

    Then in the end the title for each of the wb page is extracted to identify the insurance category and puts
    inside a python dictionary along with it's web page url.

    Args:
        soup: BeautifulSoup, a BeautifulSoup object.

    Returns:
        Dict: policy_map, A dictionary containing the urls corresponding to each insurance category.

    """
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
    """For each category of insurance products, there are multiple policies and each policy has it's
    own url. This function maps the insurance category to it's policy and the url which means that this
    function takes a insurance-category vs web-page dictionary as the argument and returns a nested python 
    dictionary that contains insurance-category, the corresponding policies and the urls. The form of the dictionary
    will be like: 
    {'insurance-category1': {'plan1': 'url1', 'plan2': 'url2'}, 'insurance-category2': {'plan1': 'url1', 'plan2': 'url2'}} 

    Pass each webpage url through a soup object to parse the html elements. In a dictionary comprehension
    extract the urls for each policy with certain filters in place and map it with the product caregory.

    Args: 
        policyPage: Dict, a dictionary containing the insurance-product and the their webpage url.

    Returns:
        Dict: policy_links, a python dictionary containing insurance-product and it's policies with the 
        urls.
    """
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



