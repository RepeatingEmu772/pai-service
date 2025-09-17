from app.config.config import settings
import logging
from enum import Enum

from langchain_postgres import PGEngine, PGVectorStore
from langchain_openai import OpenAIEmbeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class VectorSize(Enum):
    OPENAI = 3072

class EmbeddingModel(Enum):
    OPENAI = "text-embedding-3-large"

CONNECTION_STRING = settings.pg_connect_str


def get_embedding_model(client: str) -> EmbeddingModel:
    if client == "openai":
        return OpenAIEmbeddings(
            model=EmbeddingModel.OPENAI,
            openai_api_key=settings.openai_api_key
            )
    else:
        raise ValueError(f"Unsupported embedding client: {client}")

def fetch_data(table_name: str = "md_collection", query: str = ""):
    if query == "":
        logging.warning("Empty query provided to fetch_data")
        return []
    
    logging.info("Fetching data...")
    
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
    
