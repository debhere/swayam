import os
import sys
import logging

from pathlib import Path
from datetime import datetime

from app.config import constants

LOG_FILE_NAME: str = f"{datetime.now().strftime('%d_%b_%Y_%H_%M_%S')}.log"
ROOT_DIR: str = Path(__file__).resolve().parents[2]
LOG_BASE_DIR: str = constants.BASE_LOG_DIR
LOG_DESTINATION_DIR: str = f"{datetime.now().strftime('%d%m%y')}"
LOG_FILE_PATH: str = os.path.join(ROOT_DIR, constants.BASE_LOG_DIR, LOG_DESTINATION_DIR, LOG_FILE_NAME)

Path(f"{ROOT_DIR}/{LOG_BASE_DIR}/{LOG_DESTINATION_DIR}").mkdir(parents=True, exist_ok=True)

def setup_logging():
    root = logging.getLogger()

    if root.handlers:
        return

    root.setLevel(logging.INFO)
    fmt = logging.Formatter("[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)

    root.addHandler(console)
    root.addHandler(file_handler)

setup_logging()

logger = logging.getLogger(__name__)

    