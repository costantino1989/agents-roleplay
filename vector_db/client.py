import chromadb
import os
from chromadb.api.models.Collection import Collection
from typing import Any, Dict, List, Optional


class GenzeloVectorDB:
    """
    A wrapper class to interact with the Genzelo ChromaDB knowledge base.
    """

    def __init__(self, persist_path: str = ".chroma_db", collection_name: str = "genzelo_kb"):
        """
        Initialize the ChromaDB client and embedding function.

        Args:
            persist_path (str): Path to the persistent ChromaDB directory. Defaults to "chroma_db".
            collection_name (str): Name of the collection to use. Defaults to "genzelo_kb".
        """
        self.persist_path = persist_path
        self.collection_name = collection_name

        # Initialize the persistent client
        # We need to ensure we are pointing to the correct path where the DB was created.
        if not os.path.exists(self.persist_path):
            raise FileNotFoundError(f"ChromaDB persistence directory not found at: {self.persist_path}")

        self.client = chromadb.PersistentClient(path=self.persist_path)

    def get_collection(self) -> Collection:
        """
        Retrieve the 'genzelo_kb' collection.

        Returns:
            chromadb.Collection: The ChromaDB collection object.
        """
        return self.client.get_collection(
            name=self.collection_name,
        )

    def search(self,
               query_text: str,
               n_results: int = 5,
               where: Optional[Dict[str, Any]] = None,
               where_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search the collection for documents similar to the query text.

        Args:
            query_text (str): The text to search for.
            n_results (int): The number of results to return. Defaults to 5.
            where (Optional[Dict[str, Any]]): Metadata filter. 
                Used to filter results based on metadata fields (e.g., 'generation', 'country').
                
                Examples:
                    # Filter by generation 'genz'
                    where={"generation": "genz"}
                    
                    # Filter by country 'Italy'
                    where={"country": "Italy"}
                    
                    # Filter by generation 'millenials' AND country 'France' (implicit AND)
                    where={"generation": "millenials", "country": "France"}
                    
                    # Using operators ($eq, $ne, $gt, $gte, $lt, $lte, $in, $nin)
                    # Generation is either genz OR millenials
                    where={"generation": {"$in": ["genz", "millenials"]}}
                    
            where_document (Optional[Dict[str, Any]]): Document content filter.
                Used to filter results based on the content of the document text itself.
                
                Examples:
                    # Document must contain the string "work"
                    where_document={"$contains": "work"}
                    
                    # Document must NOT contain the string "salary" (logical NOT is not directly supported 
                    # in where_document at top level typically, but usually relies on $contains)
                    # ChromaDB supports $contains and logical operators $or, $and on top.
                    
                    # Document contains "flexible" OR "remote"
                    where_document={"$or": [{"$contains": "flexible"}, {"$contains": "remote"}]}

        Returns:
            Dict[str, Any]: A dictionary containing the search results (ids, documents, metadatas, distances).
        """
        collection = self.get_collection()

        return collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
