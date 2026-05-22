import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from ingestion.fetch_ecfr import fetch_all_parts, OSHA_PARTS
from ingestion.parse_cfr import parse_ecfr_xml
from ingestion.chunk_documents import build_documents
from vectorstore.build_index import build_vectorstore, load_vectorstore
from rag.chain import build_rag_chain, query_osha

FAISS_DIR = "data/faiss_osha_all"

def run_ingestion_pipeline():
    print("=" * 60)
    print("FULL OSHA CFR INGESTION PIPELINE")
    print("=" * 60)

    # Step 1: Fetch all parts
    print("\n[1/4] Fetching all OSHA CFR parts from eCFR...")
    parts = fetch_all_parts()

    # Step 2: Parse all parts
    print("\n[2/4] Parsing all parts...")
    all_sections = []
    for p in parts:
        sections = parse_ecfr_xml(str(p["path"]))
        print(f"  Part {p['part']}: {len(sections)} sections")
        all_sections.extend(sections)
    print(f"  TOTAL: {len(all_sections)} sections across all parts")

    # Step 3: Chunk all sections
    print("\n[3/4] Chunking all sections...")
    documents = build_documents(all_sections)
    print(f"  TOTAL: {len(documents)} chunks created")

    # Step 4: Embed and store
    print("\n[4/4] Embedding and storing in FAISS...")
    vectorstore = build_vectorstore(documents)
    print("\nPipeline complete! Full OSHA vector store ready.")
    return vectorstore

def run_chatbot(vectorstore=None):
    if vectorstore is None:
        vectorstore = load_vectorstore()

    chain = build_rag_chain(vectorstore)

    print("\n" + "=" * 60)
    print("FULL OSHA REGULATORY CHATBOT")
    print("Covers: 29 CFR Parts 1903, 1904, 1910, 1915, 1926")
    print("Type 'exit' to quit | 'clear' to reset conversation")
    print("=" * 60)
    print("\nExample questions:")
    print("  1. What are the PPE requirements for eye protection?")
    print("  2. When is lockout/tagout required?")
    print("  3. What are the fall protection requirements in construction?")
    print("  4. How do I record a workplace injury on the OSHA 300 log?")
    print("  5. What are the scaffolding requirements for construction?")
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