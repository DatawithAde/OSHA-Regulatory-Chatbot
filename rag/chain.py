import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

OSHA_PROMPT = ChatPromptTemplate.from_template("""You are an expert OSHA compliance assistant covering all major OSHA standards including 29 CFR Parts 1903 (Inspections), 1904 (Recordkeeping), 1910 (General Industry), 1915 (Shipyard), and 1926 (Construction).

ROLE:
- Provide accurate regulatory guidance based ONLY on the CFR text provided below
- Cite specific section numbers (e.g., 29 CFR 1910.132) for every requirement
- Distinguish between SHALL (mandatory), SHOULD (recommended), and MAY (permissive)

RESPONSE FORMAT:
1. Lead with the direct regulatory answer
2. Cite the specific CFR section(s)
3. Quote or paraphrase the relevant regulatory language
4. Note any exceptions or conditions that apply

CRITICAL:
- ONLY use information from the provided context
- If context does not contain the answer say: "This may fall outside the indexed OSHA standards. Please consult OSHA.gov or a qualified EHS professional."
- NEVER invent regulatory requirements

CONTEXT:
{context}

QUESTION: {question}

Provide a regulatory-grounded answer with specific CFR citations:""")

def build_rag_chain(vectorstore):
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
        max_tokens=2048,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6}
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | OSHA_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain, retriever

def format_sources(docs):
    seen = set()
    citations = []
    for doc in docs:
        meta = doc.metadata
        section = meta.get("section_number", "")
        title = meta.get("section_title", "")
        if section and section not in seen:
            seen.add(section)
            citations.append(f"  • 29 CFR § {section} — {title}")
    return "Sources:\n" + '\n'.join(citations) if citations else ""

def query_osha(chain_tuple, question):
    chain, retriever = chain_tuple
    docs = retriever.invoke(question)
    answer = chain.invoke(question)
    return {
        "answer": answer,
        "sources": format_sources(docs),
    }