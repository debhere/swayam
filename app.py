import sys

from utils.exception import CustomException
from utils.logger import logging

from src.pipeline import rag_pipeline

import gradio as gr

if __name__ == "__main__":
    try:
        logging.info("Launching app...")

        gr.ChatInterface(fn=rag_pipeline.answer_question).launch()
    except Exception as e:
        raise CustomException(e, sys)
