import chromadb
import json
import os
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions

# List of European countries (from extraction_and_create_kb.ipynb)
EUROPE_COUNTRIES = [
    'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
    'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia',
    'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland',
    'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
    'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia',
    'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'San Marino', 'Serbia',
    'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine',
    'United Kingdom', 'Vatican City'
]


def extract_countries(metadata_list):
    """
    Extracts countries from the metadata list based on the EUROPE_COUNTRIES list.
    Returns a comma-separated string of countries found.
    """
    found_countries = []
    # Normalize check to ensure case matching if needed, though list seems capitalized
    # The json sample shows "Austria", "Belgium" capitalized.

    for item in metadata_list:
        if item in EUROPE_COUNTRIES:
            found_countries.append(item)

    if not found_countries:
        return "Unknown"

    return ", ".join(found_countries)


def create_kb():
    # 1. Initialize Chroma Client
    # We use a persistent client to save data to disk
    persist_path = "./.chroma_db"
    client = chromadb.PersistentClient(path=persist_path)

    # 2. Setup Embedding Function
    # User requested 'intfloat/multilingual-e5-large'
    # This requires sentence_transformers to be installed.
    print("Initializing embedding function (intfloat/multilingual-e5-large)...")
    try:
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="intfloat/multilingual-e5-large"
        )
    except Exception as e:
        print(f"Error initializing SentenceTransformerEmbeddingFunction: {e}")
        print("Please ensure 'sentence-transformers' is installed: pip install sentence-transformers")
        return

    # 3. Create or Get Collection
    # "devi usare la cousine per lo score" -> {"hnsw:space": "cosine"}
    collection_name = "genzelo_kb"

    # Delete if exists to start fresh (optional, but ensures clean state for this script)
    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except ValueError:
        pass  # Collection didn't exist
    except NotFoundError:
        pass  # Collection didn't exist

    collection = client.create_collection(
        name=collection_name,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"Created collection '{collection_name}' with cosine similarity.")

    # 4. Process Files
    data_files = {
        "genz": "data/genz.json",
        "millenials": "data/millenials.json"
    }

    total_docs = 0

    for gen_key, file_path in data_files.items():
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found. Skipping.")
            continue

        print(f"Processing {file_path}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ids = []
        documents = []

        for idx, entry in enumerate(data):
            doc_text = entry.get("doc")
            original_metadata_list = entry.get("metadata", [])

            if not doc_text:
                continue

            # Extract info
            countries_str = extract_countries(original_metadata_list)

            # Prepend generation and countries to the document text as requested
            formatted_doc = f"Generation: {gen_key}\nCountries: {countries_str}\n\n{doc_text}"

            # Create a unique ID
            unique_id = f"{gen_key}_{idx}"

            ids.append(unique_id)
            documents.append(formatted_doc)

        if ids:
            collection.add(
                ids=ids,
                documents=documents
            )
            count = len(ids)
            total_docs += count
            print(f"Added {count} documents from {gen_key}.")

    print(f"Finished. Total documents in collection: {total_docs}")
    print(f"ChromaDB saved to {persist_path}")


if __name__ == "__main__":
    create_kb()
