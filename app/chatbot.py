import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from ingestion.fetch_ecfr import fetch_full_text_xml
from ingestion.parse_cfr import parse_ecfr_xml
from ingestion.chunk_documents import build_documents
from vectorstore.build_index import build_vectorstore, load_vectorstore
from rag.chain import build_rag_chain, query_osha

XML_PATH = "data/raw/cfr_29_part1910.xml"
FAISS_DIR = "data/faiss_osha_1910"

def run_ingestion_pipeline():
    print("=" * 60)
    print("OSHA 29 CFR 1910 INGESTION PIPELINE")
    print("=" * 60)

    if not Path(XML_PATH).exists():
        print("\n[1/4] Fetching 29 CFR Part 1910 from eCFR...")
        fetch_full_text_xml()
    else:
        print(f"\n[1/4] Using cached XML: {XML_PATH}")

    print("\n[2/4] Parsing XML into sections...")
    sections = parse_ecfr_xml(XML_PATH)
    print(f"  -> {len(sections)} sections parsed")

    print("\n[3/4] Chunking sections...")
    documents = build_documents(sections)
    print(f"  -> {len(documents)} chunks created")

    print("\n[4/4] Embedding and storing in FAISS...")
    vectorstore = build_vectorstore(documents)

    print("\nPipeline complete! Vector store ready.")
    return vectorstore

def run_chatbot(vectorstore=None):
    if vectorstore is None:
        vectorstore = load_vectorstore()

    chain = build_rag_chain(vectorstore)

    print("\n" + "=" * 60)
    print("OSHA REGULATORY CHATBOT - 29 CFR Part 1910")
    print("Type 'exit' to quit | 'clear' to reset conversation")
    print("=" * 60)
    print("\nExample questions:")
    print("  1. What are the PPE requirements for eye protection?")
    print("  2. When is lockout/tagout required?")
    print("  3. What training is required for forklift operators?")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() == 'exit':
            break
        if user_input.lower() == 'clear':
            chain.memory.clear()
            print("Conversation cleared.\n")
            continue

        print("\nOSHA Bot: thinking...\n")
        result = query_osha(chain, user_input)
        print(f"OSHA Bot:\n{result['answer']}")
        if result['sources']:
            print(f"\n{result['sources']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        run_chatbot()
    else:
        vs = run_ingestion_pipeline()
        run_chatbot(vs)