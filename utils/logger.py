import logging
import os
from datetime import datetime
from utils import config

LOG_FILE: str = f"{datetime.now().strftime('%d_%b_%Y_%H_%M_%S')}.log"
LOG_DATE_FOLDER: str = f"{datetime.now().strftime('%Y%m%d')}"
LOG_FOLDER: str = os.path.join(os.getcwd(), config.LOGS, LOG_DATE_FOLDER)

os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE_PATH: str = os.path.join(LOG_FOLDER, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)