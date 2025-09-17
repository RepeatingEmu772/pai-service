from app.config.config import settings
import logging
from enum import Enum

from langchain_postgres import PGEngine, PGVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class VectorSize(Enum):
    OPENAI = 3072

class EmbeddingModel(Enum):
    OPENAI = "text-embedding-3-large"

CONNECTION_STRING = settings.pg_connect_str


def get_embedding_model(client: str) -> OpenAIEmbeddings:
    if client == "openai":
        return OpenAIEmbeddings(
            model=EmbeddingModel.OPENAI.value,
            api_key=settings.openai_api_key,
        )
    else:
        raise ValueError(f"Unsupported embedding client: {client}")

def fetch_data(table_name: str = "md_collection", query: str = ""):
    if query == "":
        logging.warning("Empty query provided to fetch_data")
        return []
        
    engine = PGEngine.from_connection_string(url=CONNECTION_STRING)

    try:
        store = PGVectorStore.create_sync(
        engine=engine,
        table_name=table_name,
        embedding_service=get_embedding_model("openai"),
        )

    except Exception as e:
        logging.error(f"Error accessing vectorstore table: {e}")
        return []
    
    results = store.similarity_search(query, k=3)
    logging.info(f"Fetched {len(results)} results")
    return results


def _join_docs(docs) -> str:
    parts = []
    for d in docs:
        h1 = d.metadata.get("Header 1") or ""
        h2 = d.metadata.get("Header 2") or ""
        header = " — ".join([x for x in [h1, h2] if x])
        body = d.page_content.strip()
        parts.append(f"[{header}]\n{body}")
    return "\n\n".join(parts)


def fetch_answer(query: str, table_name: str = "md_collection", k: int = 4,
                 model: str = "gpt-4.1-mini", temperature: float = 0.4) -> dict:

    if not query:
        logging.warning("Empty query provided to fetch_answer")
        return {"answer": "", "sources": []}

    docs = fetch_data(table_name=table_name, query=query)
    if not docs:
        return {"answer": "I couldn't find anything relevant in the knowledge base.", "sources": []}

    context = _join_docs(docs[:k])

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Use ONLY the provided context to answer.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer concisely. If the context is insufficient, say so."
    )

    llm = ChatOpenAI(model=model, temperature=temperature, api_key=settings.openai_api_key)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": query}).strip()

    #  Remove later
    sources = []
    for d in docs[:k]:
        sources.append({
            "header_1": d.metadata.get("Header 1") or d.metadata.get("section"),
            "header_2": d.metadata.get("Header 2") or d.metadata.get("subsection"),
            "preview": (d.page_content or "").strip()[:180]
        })

    logging.info("Generated answer with %d sources", len(sources))
    return {"answer": answer, "sources": sources}
