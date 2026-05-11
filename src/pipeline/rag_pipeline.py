import os
import sys

from dotenv import load_dotenv

from utils import config
from utils.exception import CustomException
from utils.logger import logging

from src.vector import store

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


 
def get_retriever(existing=True):
    """The function returns an existing retreiver object by default. If vector database is not yet
    created or asked otherwise, it calls store.py to create/override the vector database first and then
    returns retriever object

    Args:
        existing: bool, by default existing is returned

    Returned:
        retriver object
    """
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
    """Using ChatOpenAI api call, an llm object is created and returned. OPENAI api key has to be present
    in the environment variable.

    Args:
        None

    Returns:
        llm object.
    """
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
    

def convert_history(gradio_history):
    messages = []
    for human, ai in gradio_history:
        messages.append(HumanMessage(content=human))
        messages.append(AIMessage(content=ai))
    return messages



def answer_question(question: str, history) -> str:
    """This is the call back function to be called from user questions. Here are the steps:

    i) A retriever object is obtained from the existing vector store.
    ii) Accordingly corresponding documents are retrieved from the database.
    iii) Context is set with the information fetched from database.
    iv) system prompt is compiled.
    v) llm is invoked with the system prompt and the user question.
    vi) llm response is returned.

    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        system_prompt = get_system_prompt().format(context=context)
        # history_messages = convert_history(history)

        llm = get_llm()

        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
        # response = llm.invoke([SystemMessage(content=system_prompt)] + history_messages + 
        #                       [HumanMessage(content=question)])
        return response.content
    except Exception as e:
        CustomException(e, sys)



