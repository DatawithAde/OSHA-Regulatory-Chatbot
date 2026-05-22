# OSHA Regulatory Chatbot

AI-powered chatbot for 29 CFR Part 1910 General Industry Standards using RAG + LangChain + GPT-4o.

## Stack
- LangChain
- FAISS vector store
- OpenAI GPT-4o + text-embedding-3-small
- Streamlit UI
- Data: 29 CFR Part 1910 via eCFR API

## Setup
1. Clone the repo
2. pip install -r requirements.txt
3. Add your OPENAI_API_KEY to a .env file
4. python app/chatbot.py --build
5. streamlit run app/streamlit_app.py
