import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv

load_dotenv()

FAISS_DIR = "./data/faiss_osha_1910"

def get_embeddings():
    print("Using OpenAI text-embedding-3-small")
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

def build_vectorstore(documents: List[Document], batch_size=100):
    embeddings = get_embeddings()
    print(f"Embedding {len(documents)} chunks into FAISS...")

    vectorstore = None

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(documents) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)

    Path(FAISS_DIR).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(FAISS_DIR)
    print(f"Vector store saved to {FAISS_DIR}")
    return vectorstore

def load_vectorstore():
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"Loaded FAISS vector store from {FAISS_DIR}")
    return vectorstore