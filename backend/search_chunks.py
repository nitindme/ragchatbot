"""
Search through all ChromaDB chunks for specific keywords
"""
import chromadb
from chromadb.config import Settings

# Connect to ChromaDB
client = chromadb.HttpClient(
    host="localhost",
    port=8001,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection("documents")

# Get all chunks
results = collection.get(include=["documents", "metadatas"])

print(f"\n✅ Total chunks in database: {len(results['documents'])}")

# Search for specific keywords
keywords = ["dress", "uniform", "wear", "attire", "clothing", "khaki"]

print(f"\n🔍 Searching for keywords: {keywords}\n")

found_any = False
for keyword in keywords:
    print(f"\n{'='*60}")
    print(f"Searching for: '{keyword}'")
    print(f"{'='*60}")
    
    found_count = 0
    for i, doc in enumerate(results['documents']):
        if keyword.lower() in doc.lower():
            found_count += 1
            found_any = True
            print(f"\n✅ Found in chunk {i+1}:")
            print(f"Metadata: {results['metadatas'][i]}")
            
            # Find the context around the keyword
            doc_lower = doc.lower()
            pos = doc_lower.find(keyword.lower())
            start = max(0, pos - 200)
            end = min(len(doc), pos + 300)
            context = doc[start:end]
            
            print(f"Context: ...{context}...")
            print("-" * 60)
    
    print(f"Total occurrences of '{keyword}': {found_count}")

if not found_any:
    print(f"\n❌ None of the keywords {keywords} found in any chunks!")
    print(f"\nℹ️  This suggests:")
    print(f"   1. The PDF may not contain dress code information")
    print(f"   2. OCR extraction failed for those pages")
    print(f"   3. Different terminology is used (try manual search in PDF)")
else:
    print(f"\n✅ Search complete! Found relevant chunks above.")
