# 🦺 OSHA Regulatory Chatbot

AI-powered chatbot for OSHA compliance questions, grounded in actual federal regulatory text using RAG + LangChain + GPT-4o.

## Live Demo
[Launch the chatbot](https://osha-regulatory-chatbot-8w6bclznjxtztzpzu9mxlx.streamlit.app/)

## Coverage
- **29 CFR Part 1903** — Inspections, Citations and Proposed Penalties
- **29 CFR Part 1904** — Recording and Reporting Occupational Injuries
- **29 CFR Part 1910** — General Industry Standards
- **29 CFR Part 1915** — Shipyard Employment
- **29 CFR Part 1926** — Construction Safety

## Features
- Answers OSHA compliance questions with exact CFR section citations
- Distinguishes between SHALL (mandatory), SHOULD (recommended), and MAY (permissive)
- Covers 1000+ regulatory sections across all major OSHA standards
- Built with Retrieval-Augmented Generation (RAG) for citation-accurate answers

## Stack
- **LangChain** — RAG orchestration
- **FAISS** — Vector store for semantic search
- **OpenAI GPT-4o** — Answer generation
- **OpenAI text-embedding-3-small** — Document embeddings
- **Streamlit** — Web UI
- **eCFR API** — Live federal regulatory data source

## Architecture
eCFR API → XML Parser → Regulatory Chunker → FAISS Vector Store
                                                      ↓
                    User Query → Semantic Retrieval → GPT-4o → Cited Answer

## Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. Create `.env` file with `OPENAI_API_KEY=your-key`
4. `python app/chatbot.py` to build index and start chatbot
5. `streamlit run app/streamlit_app.py` for web UI

## Author
Adeyemi Samuel Ayorinde — EHS Data Scientists, University of Arkansas at Little Rock
