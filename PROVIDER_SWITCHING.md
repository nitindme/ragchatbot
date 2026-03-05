# Switching Between OpenAI and Ollama

## The Problem: Different Embedding Dimensions

**Why can't we have uniform dimensions?**

Different embedding models produce **fixed** dimension sizes that cannot be changed:

| Provider | Model | Dimensions | Can Change? |
|----------|-------|------------|-------------|
| OpenAI | text-embedding-3-small | 1536 | ❌ No |
| Ollama | nomic-embed-text | 768 | ❌ No |

**Why dimensions can't be unified:**

1. **Model Architecture** 🏗️: Neural network size is hardcoded
2. **Semantic Meaning** 🧠: Each dimension represents learned features
3. **Vector Math** ➗: ChromaDB's similarity search requires exact dimensions

Padding or truncating would **break the semantic relationships** between vectors!

---

## The Solution: Separate Collections Per Provider

Instead of trying to unify dimensions, we use **provider-specific collections**:

```
ChromaDB:
├── documents_openai (1536-dim)  ← OpenAI embeddings
└── documents_ollama (768-dim)   ← Ollama embeddings
```

**Benefits:**
- ✅ No collection deletion when switching
- ✅ Each provider keeps its own embeddings
- ✅ Compare quality side-by-side
- ✅ Zero downtime switching
- ✅ Upload documents once per provider

---

## How to Switch Providers

### Method 1: Using the Script (Recommended)

```bash
# Switch to OpenAI
cd backend
python switch_provider.py openai

# Switch to Ollama
python switch_provider.py ollama
```

The script:
1. Updates `LLM_PROVIDER` in `.env`
2. Shows collection information
3. Displays next steps
4. Backend auto-reloads (if running with `--reload`)

### Method 2: Manual Switch

Edit `backend/.env`:

```properties
# For OpenAI
LLM_PROVIDER=openai

# For Ollama
LLM_PROVIDER=ollama
```

Backend will auto-reload and use the correct collection: `documents_{provider}`

---

## First Time Setup

### OpenAI Setup

1. Ensure API key is set in `.env`:
   ```properties
   OPENAI_API_KEY=sk-proj-...
   ```

2. Switch to OpenAI:
   ```bash
   python switch_provider.py openai
   ```

3. Upload documents via admin UI (http://localhost:3000)
   - Documents will be embedded with 1536 dimensions
   - Stored in `documents_openai` collection

### Ollama Setup

1. Start Ollama container:
   ```bash
   docker-compose up -d ollama
   ```

2. Pull required models:
   ```bash
   docker exec -it rag-ollama ollama pull llama3.2:1b
   docker exec -it rag-ollama ollama pull nomic-embed-text
   ```

3. Update `.env` for local Ollama (if running backend outside Docker):
   ```properties
   OLLAMA_URL=http://localhost:11434
   ```

4. Switch to Ollama:
   ```bash
   python switch_provider.py ollama
   ```

5. Upload documents via admin UI
   - Documents will be embedded with 768 dimensions
   - Stored in `documents_ollama` collection

---

## Collection Management

### Check Active Collection

The active collection is determined by `LLM_PROVIDER`:

```python
# In config.py
@property
def chroma_collection_name(self) -> str:
    return f"{self.CHROMA_COLLECTION}_{self.LLM_PROVIDER}"

# Examples:
LLM_PROVIDER=openai → documents_openai
LLM_PROVIDER=ollama → documents_ollama
```

### View All Collections

```python
# In Python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8001)
collections = client.list_collections()
for col in collections:
    print(f"{col.name}: {col.count()} documents")
```

### Delete a Specific Collection

```python
# Delete OpenAI collection
client.delete_collection("documents_openai")

# Delete Ollama collection
client.delete_collection("documents_ollama")
```

---

## Cost & Performance Comparison

| Aspect | OpenAI | Ollama |
|--------|--------|--------|
| **Cost** | ~$0.0001 per 1K tokens | Free (local) |
| **Speed** | ~1-2 seconds | ~3-5 seconds |
| **Quality** | Higher accuracy | Good for basic tasks |
| **Setup** | API key only | Requires Docker |
| **Privacy** | Data sent to OpenAI | Fully local |
| **Models** | gpt-4o-mini, gpt-4 | llama3.2:1b, llama3:8b |

**Recommendation:**
- **Development**: Ollama (free, local)
- **Production**: OpenAI (better quality, faster)
- **Privacy-sensitive**: Ollama (data stays local)

---

## Troubleshooting

### "Collection expecting dimension X, got Y"

**Cause**: Switching providers without using separate collections

**Fix**: 
```bash
# Update to use provider-specific collections
git pull  # Get latest code with collection fix
python switch_provider.py [provider]
```

### "Failed to connect to Ollama"

**Cause**: Ollama container not running or wrong URL

**Fix**:
```bash
# Start Ollama
docker-compose up -d ollama

# If running backend locally, update .env:
OLLAMA_URL=http://localhost:11434
```

### "Could not connect to Chroma server"

**Cause**: ChromaDB container not running or wrong URL

**Fix**:
```bash
# Start ChromaDB
docker-compose up -d chroma

# If running backend locally, update .env:
CHROMA_URL=http://localhost:8001
```

### "Empty responses from chatbot"

**Cause**: Documents not uploaded to current provider's collection

**Fix**:
1. Check which provider is active: `cat backend/.env | grep LLM_PROVIDER`
2. Upload documents via admin UI
3. Documents must be uploaded separately for each provider

---

## Technical Details

### How It Works

1. **Config**: `chroma_collection_name` property generates provider-specific name
2. **Document Service**: Uses `settings.chroma_collection_name` to get/create collection
3. **Embeddings**: Each provider uses its own embedding model with native dimensions
4. **Storage**: ChromaDB stores collections with appropriate dimensional metadata

### Code Implementation

```python
# config.py
@property
def chroma_collection_name(self) -> str:
    """Get collection name with provider suffix."""
    return f"{self.CHROMA_COLLECTION}_{self.LLM_PROVIDER}"

# document_service.py
collection_name = settings.chroma_collection_name
self.collection = self.chroma_client.get_or_create_collection(
    name=collection_name
)
```

### Why This Design?

**Alternative 1**: Delete and recreate collection on switch
- ❌ Loses all uploaded documents
- ❌ Downtime during transition
- ❌ Need to re-upload on every switch

**Alternative 2**: Store dimension-agnostic data
- ❌ Impossible - embeddings ARE dimensional vectors
- ❌ Would break vector similarity search
- ❌ No mathematical way to unify dimensions

**Our Design** (Separate Collections):
- ✅ Zero data loss
- ✅ Instant switching
- ✅ Preserves embeddings per provider
- ✅ Mathematically sound

---

## Summary

**Question**: Why can't we have uniform embedding dimensions?

**Answer**: Embedding dimensions are **hardcoded** in the model architecture and represent learned semantic features. Changing them would destroy the meaning of the vectors.

**Solution**: Use separate collections per provider (`documents_openai` and `documents_ollama`) so each can maintain embeddings in their native dimensions.

**Usage**: 
```bash
python switch_provider.py [openai|ollama]
```

**Result**: Seamless provider switching with no data loss! 🎉
