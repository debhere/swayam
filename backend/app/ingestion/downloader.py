import sys

from app.ingestion.insurance import download_insurance_docs
from app.ingestion.other_products import download_other_product_docs

from app.config import constants

from app.utils.exception import CustomException
from app.utils.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main controller of the ingestion module. Invokes the product functions for each LIC product
    and downloads the corresponding artefacts.
    """
    try:
        base_url: str = constants.LIC_BASE_URL
        lic: str = constants.LIC_WEB

        for product, var in constants.PRODUCT_CATEGORIES.items():
            logger.info(f"Invoking {product} module...")
            if product == 'insurance':
                download_insurance_docs(base_url, var, lic)

            elif product in ['pension', 'ulp', 'mip']:
                download_other_product_docs(base_url, var, lic, product)

            elif product == 'wp':
                logger.info("Withdrawn products are not included yet...!!")
            else:
                logger.info("Unrecognized product...exiting!!")
                sys.exit(1)

    except Exception as e:
        raise CustomException(e, sys)
    


if __name__ == "__main__":
    main()