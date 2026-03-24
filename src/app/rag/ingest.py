import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import hashlib

SOURCES = [
    "https://medlineplus.gov/heartattack.html",
    "https://medlineplus.gov/stroke.html", 
    "https://medlineplus.gov/appendicitis.html",
    "https://medlineplus.gov/kidneystones.html",
    "https://medlineplus.gov/pulmonaryembolism.html",
    "https://medlineplus.gov/angina.html",
    "https://medlineplus.gov/aorticaneurysm.html",
]

def scrape(url: str) -> str:
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return " ".join(soup.get_text().split())

def chunk(text: str, size: int = 150, overlap: int = 30) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+size]))
        i += size - overlap
    return chunks

def build_vectorstore():
    ef = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="src/app/rag/chroma_db")
    collection = client.get_or_create_collection("medical_docs", embedding_function=ef)

    if collection.count() > 0:
        print("Vector store already built, skipping.")
        return collection

    for url in SOURCES:
        print(f"Scraping {url}...")
        try:
            text = scrape(url)
            chunks = chunk(text)
            ids = [hashlib.md5(f"{url}_{i}".encode()).hexdigest() for i in range(len(chunks))]
            collection.add(documents=chunks, ids=ids, metadatas=[{"source": url}] * len(chunks))
            print(f"  Added {len(chunks)} chunks")
        except Exception as e:
            print(f"  Failed: {e}")

    print("Vector store built.")
    return collection

if __name__ == "__main__":
    build_vectorstore()