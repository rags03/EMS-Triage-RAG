import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

_collection = None

def get_collection():
    global _collection
    if _collection is None:
        ef = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path="src/app/rag/chroma_db")
        _collection = client.get_or_create_collection("medical_docs", embedding_function=ef)
    return _collection

def retrieve(query: str, n: int = 5) -> str:
    collection = get_collection()
    if collection.count() == 0:
        return ""
    results = collection.query(query_texts=[query], n_results=n)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    formatted = []
    for chunk, source in zip(chunks, sources):
        formatted.append(f"[Source: {source}]\n{chunk}")
    return "\n\n".join(formatted)