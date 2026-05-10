import os
import sys

from dotenv import load_dotenv

from utils import config
from utils.exception import CustomException
from utils.logger import logging

from src.vector import build_vectorstore

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def get_retriever():
    # return vector-store.as_retriver()
    pass

def get_llm():
    pass

def answer_question(question: str, history):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    context = "\n\n".join(doc for doc in docs)
    system_prompt = system_prompt.format(context=context)

    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return response.content



