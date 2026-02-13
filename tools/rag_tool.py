import time
from utils.logger import get_logger
from vector_db.client import GenzeloVectorDB

logger = get_logger("RagTool")

def rag(generation: str, country: str, query: str, client: GenzeloVectorDB = None) -> str:
    """
    Search the knowledge base for behavioral insights about a specific generation and country.
    Use this to understand values, preferences, and behaviors to formulate better questions.
    
    Args:
        generation (str): "genz" or "millenials"
        country (str): The country (e.g., "Italy", "France")
        query (str): The specific topic to search for (e.g., "work values", "digital habits")
        client (GenzeloVectorDB, optional): The Vector DB client instance.
    """
    start_time = time.perf_counter()

    if not client:
        return "Error: Knowledge Base client not provided."

    logger.info(f"Searching for: '{query}' ({generation}, {country})")

    # Construct document content filter
    where_document_filter = {
        "$and": [
            {"$contains": generation},
            {"$contains": country}
        ]
    }

    # Perform search
    try:
        results = client.search(
            query_text=query,
            n_results=3,
            where_document=where_document_filter
        )

        documents = results.get("documents", [])
        if documents and documents[0]:
            # Chroma returns a list of lists of documents
            joined_docs = "\n\n".join(documents[0])
            result_text = f"Found insights:\n{joined_docs}"
        else:
            result_text = "No specific documents found for this query."

    except Exception as e:
        logger.error(f"Error querying VectorDB: {str(e)}")
        result_text = f"Error querying VectorDB: {str(e)}"

    end_time = time.perf_counter()
    duration = end_time - start_time
    logger.info(f"RAG Tool execution time: {duration:.4f}s")

    return result_text
