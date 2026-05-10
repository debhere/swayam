import os
import sys
import glob
import json

from typing import List, Dict
# from utils import config
from utils.exception import CustomException
from utils.logger import logging

# from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter



def load_json_with_root(file_path: str) -> JSONLoader:
    """This function takes a json filepath as argument and returns a JSONLoader object. 
    
    There are certain json attributes that need to be recorded as metadata but comes one level up than the 
    jq schema. the metadata then accordingly applied within the metadata_func inner function. In the end, 
    The JSONLoader object is returned with the content and the corresponding metadata. 

    Args:
        file_path: str, json file path.

    Returns: JSONLoader object
    """
    with open(file_path, 'r') as f:
        full_data = json.load(f)
        policy_name = full_data.get("policy_name", "unknown")
        category = full_data.get("category", "unknown")
        source = full_data.get("source_path", "unknown")
        
    def metadata_func(record: Dict, base_metadata: Dict) -> Dict:
        base_metadata["policy_name"] = policy_name
        base_metadata["category"] = category
        base_metadata["doc_type"] = record.get("page_type", "unknown")
        base_metadata['source'] = source
        return base_metadata
        
    return JSONLoader(
        file_path=file_path,
        jq_schema='.pages[] | select(.page_type == "content")', # grabbing only those pages where page_type is content
        content_key='text',
        metadata_func=metadata_func
    )


def compile_documents(source: str) -> List[Document]:
    """This function compiles the jsin texts as documents in a list

    Args:
        source: str, this is knowledge-base.

    Returns:
        documents: List[Document], list of documents i.e., pages in the json files.
    """
    try:
        folders = glob.glob(f"{source}/*")
        documents: List[Document] = []

        for folder in folders:
            loader = DirectoryLoader(folder, glob='**/*.json', loader_cls=load_json_with_root)
            folder_docs = loader.load()

            for doc in folder_docs:
                documents.append(doc)
            
        message: str = f"{len(documents)} documents are loaded"
        print(message)
        logging.info(f"{message}")
        return documents
    except Exception as e:
        raise CustomException(e, sys)
    

def create_chunks_from_documents(documents: List[Document]) -> List[Document]:
    """Documents needs to splitted into chunks prior to loading into the vectir db.

    Args:
        documents: List[Document], list of documents i.e., pages in the json files.

    Returns:
        chunks: List[Document], Each document spitted into small chunks with overlap.
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        chunks = text_splitter.split_documents(documents)
        
        print(f"{len(chunks)} chunks has been created...")
        logging.info(f"{len(chunks)} chunks has been created...")

        return chunks
    except Exception as e:
        raise CustomException(e, sys)


def get_hf_embeddings(model) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model=model)

def is_db_exists(db_name) -> bool:
    return os.path.exists(db_name)


def create_vectorstore(chunks: List[Document], db_name: str, embedding_model: str) -> Chroma:
    """Actual vector-store is created with Chroma db.

    Args:
        chunks: List[Document], overlapping chunks of documents.
        db_name: str, vector db name.
        embedding_model: str, embedding model name

    Returns:
        None
    """
    try:
        # embeddings = HuggingFaceEmbeddings(model=embedding_model)
        embeddings = get_hf_embeddings(embedding_model)
        if is_db_exists(db_name):
            Chroma(persist_directory=db_name, embedding_function=embeddings, documents=chunks).delete_collection()
            # Removes existing db collection with same db-name

        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_name)

        logging.info(f"vectorstore created with {vectorstore._collection.count()} documents")
        return vectorstore
    
    except Exception as e:
        raise CustomException(e, sys)
    

def build_vectorstore(knowledge_base: str, vector_db: str, embedding_model: str) -> Chroma:
    """The controller function of the overall vector-store creation process.

    i) Creates the documents.
    ii) Create chunks from the documents.
    iii) Create the vector-store with Chroma db

    Args:
        knowledge_base: str, knowledge-base
        vector_db: str, vector-db name
        embedding_model: str, embedding model name.

    Returns:
        OK: str, a sample string.
    """
    try:
        docs: List[Dict] = compile_documents(knowledge_base)
        logging.info("Documents are being loaded from knowledge-base...")

        chunks: List[Dict] = create_chunks_from_documents(documents=docs)
        logging.info("Documents are being splitted into chunks...")

        vectorstore = create_vectorstore(chunks=chunks, db_name=vector_db, embedding_model=embedding_model)
        return vectorstore

    except Exception as e:
        raise CustomException(e, sys)
