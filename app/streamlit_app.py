import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from vectorstore.build_index import load_vectorstore
from rag.chain import build_rag_chain, query_osha

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSHA Regulatory Chatbot",
    page_icon="🦺",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🦺 OSHA Regulatory Chatbot")
st.markdown("**Full Coverage: 29 CFR Parts 1903, 1904, 1910, 1915, 1926**")
st.markdown("Covers General Industry, Construction, Shipyard, Recordkeeping & Inspections.")
st.markdown("Ask any OSHA compliance question and get answers with exact CFR citations.")

# ── Load vectorstore and chain (cached so it only loads once) ─────────────────
@st.cache_resource
def load_chain():
    with st.spinner("Loading OSHA regulatory database..."):
        vectorstore = load_vectorstore()
        chain = build_rag_chain(vectorstore)
    return chain

chain_tuple = load_chain()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot uses **Retrieval-Augmented Generation (RAG)** to answer 
    OSHA compliance questions grounded in the actual regulatory text.
    
    **Data source:** 29 CFR Part 1910 via eCFR API  
    **Model:** GPT-4o  
    **Vector store:** FAISS  
    **Framework:** LangChain  
    """)

    st.divider()
    st.header("Example Questions")
   examples = [
    "What are the PPE requirements for eye protection?",
    "When is lockout/tagout required?",
    "What are the fall protection requirements in construction?",
    "How do I record a workplace injury on the OSHA 300 log?",
    "What are the scaffolding requirements for construction?",
    "What are the confined space entry requirements?",
    "What are the shipyard safety requirements for welding?",
    "When must an employer report a fatality to OSHA?",
]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.example_query = ex

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📋 CFR Sources"):
                st.markdown(msg["sources"])

# ── Handle example button clicks ──────────────────────────────────────────────
if "example_query" in st.session_state:
    prompt = st.session_state.pop("example_query")
else:
    prompt = st.chat_input("Ask an OSHA compliance question...")

# ── Process input ─────────────────────────────────────────────────────────────
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching 29 CFR 1910..."):
            result = query_osha(chain_tuple, prompt)

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander("📋 CFR Sources"):
                st.markdown(result["sources"])

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", "")
    })