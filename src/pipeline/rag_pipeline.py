import os
import sys

from dotenv import load_dotenv

from utils import config
from utils.exception import CustomException
from utils.logger import logging

from src.vector import store

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage


# db_name: str = config.DB_NAME
# embedding_model_hf: str = config.EMBEDDING_MODEL_HF
# chat_model: str = config.CHAT_MODEL
# knowledge_base: str = config.KNOWLEDGE_BASE

 
def get_retriever(existing=True):
    try:
        db_name = config.DB_NAME
        embedding_model_hf = config.EMBEDDING_MODEL_HF
        if store.is_db_exists(db_name=db_name) and existing:
            embeddings = store.get_hf_embeddings(model=embedding_model_hf)

            logging.info("Returning retriever from existing vector database...")
            return Chroma(persist_directory=db_name, embedding_function=embeddings).as_retriever()
        else:
            logging.info("Vector store creation initiated...")
            knowledge_base = config.KNOWLEDGE_BASE
            return store.build_vectorstore(db_name, knowledge_base, embedding_model_hf)
    except Exception as e:
        raise CustomException(e, sys)


def get_llm():
    try:
        load_dotenv(override=True)
        openai_api_key: str = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            chat_model: str = config.CHAT_MODEL
            return ChatOpenAI(model=chat_model)
    except Exception as e:
        raise CustomException(e, sys)

def get_system_prompt():
    try:
        with open("src/pipeline/prompts/system_prompt.txt", 'r') as file:
            system_prompt = file.read()
            return system_prompt
    except Exception as e:
        raise CustomException(e, sys)

def answer_question(question: str, history):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    system_prompt = get_system_prompt().format(context=context)
    llm = get_llm()

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return response.content



