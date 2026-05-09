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
        response.content: bytes, The content of the response ofject from the request. get(url) call.
    """
    try:

        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.content
    except Exception as e:
        raise CustomException(e, sys)


def getSoup(url: str) -> BeautifulSoup:
    """This is a simple function that returns a BeautifulSoup object every time invoked. The function
    takes an url of a website as an argument. It invokes the getContent() function to get the content
    of the given website. The parsed web content in the BeautifulSoup object is then returned.

    Args:
        url: str, url of a website.

    Returns:
        soup: BeautifulSoup object
    """
    try:
        content = getContent(url)
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            return soup
    except Exception as e:
        raise CustomException(e, sys)


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
        policy_map: Dict, A dictionary containing the urls corresponding to each insurance category.

    """
    try:
        elements = [elem.find('a').find_next('ul', class_='child-menu') for elem in soup.select('li.has-sub')]
        elems = set(elem.find_next('ul', class_="child-menu") for elem in elements if "Insurance" in elem.find_next('li').find_next('a')['title']\
            and "Plan" in elem.find_next('li').find_next('a')['title'])
        
        policy_map = {}

        for elem in elems:
            links = elem.find_all('a')
            for link in links:
                policy_map[link['title'].strip().replace(' ', '_')] = link['href']
                
        return policy_map
    
    except Exception as e:
        raise CustomException(e, sys)


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
        policy_links: Dict, a python dictionary containing insurance-product and it's policies with the 
        urls.
    """
    policy_links = {}
    for p, l in policyPage.items():
        soup = getSoup(l)
        policy_links[p] = {link.text.strip().replace("LIC's ", '').replace("LIC’s ", '').replace(' ', '_').replace('(', '') \
                           .replace(')', '').replace(':', ''): link['href'] \
                           for link in soup.find_all('a') if 'LIC' in link.text and 'https' not in link['href'] and 'guest' in link['href']}
    return policy_links


def getPolicyLinksPerPlan(url: str, planLinks: Dict) -> Dict:
    """Each policy has it's own policy document in a pdf file. The pdf file link has be grabbed and mapped
    with every policy and in turn for every insurance category.

    This function takes the python dictionary where the links for each plan contains. It also takes
    the base url as input because the policy urls are all relative paths and to make a complete url,
    the base url is required.

    For each policy, the policy pdf is link is being extracted and put it against each policy and then
    returns it.

    Args:
        url: string, the base url for the insurance products
        planLinks: Dict, html page link for each insurance policy.

    Returns:
        pdfLinks: Dict, a python dictionary consisting the insurance category vs policy and it's policy
        document.
    """
    try:
        pdfLinks = {}
        for plan, links in planLinks.items():
            policyMap = {}
            for policy, link in links.items():
                soup = getSoup(f"{url}/{link}")
                pdf = [link['href'] for link in soup.find_all('a') if "Policy Document" in link.text][0]
                pdf = pdf[: pdf.index('pdf') + 3]
                policyMap[policy] = pdf
            pdfLinks[plan] = policyMap
        return pdfLinks
    except Exception as e:
        raise CustomException(e, sys)



def downloadPolicyDocuments(url: str, pdfs: Dict, destination: str):
    """This function extracts the policy document for each policy and downloads it. The raw data destination
    is passed as an argument whereas the downloaded policy documents are kept within another folder as per the 
    insurance category.

    Args:
        url: string, base url for insurance products.
        pdfs: Dict, the pdf policy document link for each policy.
        destination: string, folder path to download the policy pdfs.

    Returns:
        None

    """
    for plan, policyPdfs in pdfs.items():
        for policy, pdf in policyPdfs.items():
            file_location = Path(f"{destination}/{plan.lower()}")
            if not file_location.is_dir():
                file_location.mkdir(parents=True, exist_ok=True)
            with open(f"{file_location}/{policy.lower()}.pdf", 'wb') as f:
                pdf_link = f"{url}/{pdf}"
                f.write(getContent(pdf_link))



def run(url: str, location: str) -> str:
    """This function acts like the controller. It takes the base url and the destination folder location
    as arguments.
    
    At first, it gets a soup object and gets the html pages for each insurance plan.
    Second, it passes the html pages to getInsurancePlanLinks() to get the policy links for each plan and policy.
    Then, it gets the links to each policy from getInsurancePlanLinks() function
    Once policy links known, the corresponding policy pdf links are required. getPolicyLinksPerPlan() returns the 
    same. In the end, as per the pdf links, the policy pdf documents are download.

    Args:
        url: string, base url for LIC insurance products.
        location: string, the location where the policy pdf files are to be downloaded.

    Returns:
        "OK": string, if everything is fine.
    """
    try:
        soup = getSoup(url)

        logging.info("Getting the html pages for each insurance plan...")
        plan_pages: Dict = getPagesForInsurancePlans(soup)
        
        logging.info("Policy links are being extracted...")
        plan_links: Dict = getInsurancePlanLinks(plan_pages)
        
        logging.info("Policy documents are being mapped per policy...")
        planPdfs: Dict = getPolicyLinksPerPlan(url, plan_links)

        logging.info("Policy documents downloading...")
        downloadPolicyDocuments(url, planPdfs, location)
        
        print("Download Successful")
        return "OK"
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        url: str = config.BASE_URL
        policies: str = config.RAW_DATA_FOLDER
        logging.info("Intiate scraping")
        run(url, policies)

    except Exception as e:
        raise CustomException(e, sys)



