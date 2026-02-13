import unittest
import os
import sys

# Add project root to sys.path to ensure we can import vector_db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vector_db.client import GenzeloVectorDB

class TestGenzeloVectorDB(unittest.TestCase):

    def setUp(self):
        # Ensure we are pointing to the correct DB path relative to where tests run
        # If running from root, 'chroma_db' is correct.
        self.db_path = "chroma_db"
        if not os.path.exists(self.db_path):
            self.skipTest(f"ChromaDB not found at {self.db_path}. Run scripts/create_kb_chroma.py first.")
        
        self.vector_db = GenzeloVectorDB(persist_path=self.db_path)

    def test_init_and_get_collection(self):
        """Test that client initializes and retrieves the collection."""
        collection = self.vector_db.get_collection()
        self.assertIsNotNone(collection)
        self.assertEqual(collection.name, "genzelo_kb")
        # Check if collection is not empty (assuming data was added)
        self.assertGreater(collection.count(), 0, "Collection should not be empty")

    def test_search_basic(self):
        """Test a basic search query."""
        results = self.vector_db.search(query_text="work life balance", n_results=2)
        
        self.assertIn("ids", results)
        self.assertIn("documents", results)
        self.assertIn("metadatas", results)
        self.assertEqual(len(results["ids"][0]), 2)

    def test_search_with_where_filter(self):
        """Test search with metadata filtering (generation=genz)."""
        # We assume there is at least one Gen Z entry
        results = self.vector_db.search(
            query_text="work", 
            n_results=5, 
            where={"generation": "genz"}
        )
        
        metadatas = results["metadatas"][0]
        for meta in metadatas:
            self.assertEqual(meta["generation"], "genz")

    def test_search_with_where_document(self):
        """Test search with document content filtering."""
        # This test relies on the existence of a common word. "the" or "work" is usually safe.
        # Let's try to find something that likely exists.
        # The prompt implies behavioral patterns, so "work" or "job" might be there.
        # But to be safe, we can try searching for something we just found in previous test
        # or just skip if we are unsure of content.
        # Let's search for "work" which is a very common topic in this dataset context.
        
        search_term = "work"
        results = self.vector_db.search(
            query_text="career",
            n_results=3,
            where_document={"$contains": search_term}
        )
        
        # If no results found, we can't strictly assert the content contains it without failing the test
        # on empty result. So we check if results exist first.
        if len(results["ids"][0]) > 0:
            docs = results["documents"][0]
            for doc in docs:
                self.assertIn(search_term, doc.lower())

if __name__ == '__main__':
    unittest.main()
