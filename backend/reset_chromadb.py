"""
Reset ChromaDB collection to fix dimension mismatch
Run this when switching between Ollama (768) and OpenAI (1536) embeddings
"""
import chromadb
from chromadb.config import Settings

# Connect to ChromaDB
client = chromadb.HttpClient(
    host="localhost",
    port=8001,
    settings=Settings(anonymized_telemetry=False)
)

collection_name = "documents"

try:
    # Delete the old collection
    client.delete_collection(name=collection_name)
    print(f"✅ Deleted collection '{collection_name}'")
except Exception as e:
    print(f"⚠️  Collection might not exist: {e}")

# Create new collection (it will be created with the correct dimensions on first use)
print(f"✅ Collection will be recreated with correct dimensions on next document upload")
print(f"\nℹ️  Next steps:")
print(f"   1. Start the backend")
print(f"   2. Upload a document through the admin UI")
print(f"   3. The collection will be created with OpenAI's 1536 dimensions")
