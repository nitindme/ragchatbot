# OpenAI Integration Guide

## Overview
The chatbot now supports **both OpenAI and Ollama** as LLM providers. You can easily switch between them by changing a single configuration setting.

## Quick Start - Switch to OpenAI

### 1. Get Your OpenAI API Key
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to **API Keys** section
3. Click "Create new secret key"
4. Copy your key (starts with `sk-...`)

### 2. Configure the Backend

Edit `backend/.env` file:

```bash
# Change LLM_PROVIDER from "ollama" to "openai"
LLM_PROVIDER=openai

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Choose your OpenAI model (optional, defaults shown)
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

### 3. Restart the Backend

```bash
cd /Users/nitindigraje/Documents/delhipolicechatbot
pkill -f "uvicorn"
bash start_backend_simple.sh
```

That's it! Your chatbot will now use OpenAI.

---

## Model Options

### OpenAI Models

#### **Chat Models**
| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ Fast | 💰 Low | ⭐⭐⭐ Good | **Recommended** - Best balance |
| `gpt-4o` | ⚡⚡ Medium | 💰💰 Medium | ⭐⭐⭐⭐⭐ Excellent | High-quality answers |
| `gpt-4-turbo` | ⚡⚡ Medium | 💰💰💰 High | ⭐⭐⭐⭐⭐ Excellent | Complex reasoning |
| `gpt-3.5-turbo` | ⚡⚡⚡ Fast | 💰 Very Low | ⭐⭐⭐ Good | Budget option |

#### **Embedding Models**
| Model | Speed | Cost | Quality |
|-------|-------|------|---------|
| `text-embedding-3-small` | ⚡⚡⚡ Fast | 💰 Low | ⭐⭐⭐ Good (Recommended) |
| `text-embedding-3-large` | ⚡⚡ Medium | 💰💰 Medium | ⭐⭐⭐⭐ Better |

### Ollama Models (Local/Free)

| Model | Speed | Memory | Quality |
|-------|-------|--------|---------|
| `llama3.2:1b` | ⚡⚡⚡ Very Fast | 1.3 GB | ⭐⭐⭐ Good |
| `llama3:8b` | ⚡ Slow | 4.7 GB | ⭐⭐⭐⭐ Very Good |
| `llama3:70b` | 🐌 Very Slow | 40 GB | ⭐⭐⭐⭐⭐ Excellent |

---

## Comparison: OpenAI vs Ollama

| Feature | OpenAI | Ollama (Local) |
|---------|--------|----------------|
| **Cost** | Pay per use (~$0.10-1.00 per 1M tokens) | Free (after initial setup) |
| **Speed** | Very fast (1-3 seconds) | Slower (2-30 seconds depending on model) |
| **Quality** | Excellent | Good to Very Good |
| **Privacy** | Data sent to OpenAI servers | 100% private (runs locally) |
| **Setup** | API key only | Docker + model downloads |
| **Internet** | Required | Not required |
| **Memory** | None (cloud-based) | 1-40 GB depending on model |

### When to Use OpenAI:
- ✅ Need fastest possible responses
- ✅ Want highest quality answers
- ✅ Don't want to manage infrastructure
- ✅ Budget allows for API costs
- ✅ Internet connection is reliable

### When to Use Ollama:
- ✅ Privacy is critical (sensitive documents)
- ✅ Want zero per-query costs
- ✅ Have sufficient local hardware
- ✅ Need offline capability
- ✅ Want complete control

---

## Configuration Examples

### Example 1: Fast & Cheap (OpenAI)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini              # Fast & cheap
OPENAI_EMBED_MODEL=text-embedding-3-small
```

### Example 2: High Quality (OpenAI)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o                    # Best quality
OPENAI_EMBED_MODEL=text-embedding-3-large
```

### Example 3: Private & Fast (Ollama)
```bash
LLM_PROVIDER=ollama
OLLAMA_LLM_MODEL=llama3.2:1b          # Fast local model
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### Example 4: Private & High Quality (Ollama)
```bash
LLM_PROVIDER=ollama
OLLAMA_LLM_MODEL=llama3:8b            # Better quality, slower
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## Testing Your Configuration

After changing settings, test with a simple question:

1. Go to http://localhost:3001 (Chat UI)
2. Ask: "What is the dress code for training?"
3. Check response time and quality

**Expected Response Times:**
- OpenAI (`gpt-4o-mini`): 1-3 seconds
- Ollama (`llama3.2:1b`): 2-5 seconds  
- Ollama (`llama3:8b`): 10-30 seconds

---

## Troubleshooting

### OpenAI Errors

**Error: "OPENAI_API_KEY not configured"**
- Make sure you set `OPENAI_API_KEY` in `.env`
- Remove the placeholder text
- Restart the backend

**Error: "Incorrect API key"**
- Check your API key at https://platform.openai.com/api-keys
- Make sure it starts with `sk-`
- No extra spaces or quotes

**Error: "Rate limit exceeded"**
- You've exceeded your OpenAI usage limits
- Check your OpenAI account dashboard
- Upgrade your plan or wait for reset

### Switching Back to Ollama

If you want to switch back to local Ollama:

```bash
# Edit backend/.env
LLM_PROVIDER=ollama
OLLAMA_LLM_MODEL=llama3.2:1b

# Restart
pkill -f "uvicorn"
bash start_backend_simple.sh
```

---

## Cost Estimation (OpenAI)

### Typical Usage Costs with `gpt-4o-mini`:

| Usage | Tokens | Cost (USD) |
|-------|--------|------------|
| 1 chat message | ~1,000 | $0.0001 |
| 100 chat messages | ~100K | $0.01 |
| 1,000 chat messages | ~1M | $0.10 |
| 10,000 chat messages | ~10M | $1.00 |

**Notes:**
- Prices are approximate for `gpt-4o-mini`
- `gpt-4o` is 10-20x more expensive
- Embeddings are separate but cheaper (~$0.02 per 1M tokens)
- Check current pricing at https://openai.com/pricing

---

## Security Best Practices

### Protecting Your API Key:

1. **Never commit `.env` file to git**
   ```bash
   # Already in .gitignore, but verify:
   cat .gitignore | grep .env
   ```

2. **Use environment variables in production**
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. **Rotate keys regularly**
   - Create new key every few months
   - Delete old keys from OpenAI dashboard

4. **Set spending limits**
   - Go to OpenAI dashboard → Billing
   - Set monthly budget limits

---

## Summary

✅ **Easy to switch**: Just change `LLM_PROVIDER` in `.env`  
✅ **Both providers work**: OpenAI for speed, Ollama for privacy  
✅ **Flexible**: Mix and match models based on your needs  
✅ **Tested**: Both integrations fully working with citations  

Need help? Check the main README.md or open an issue!
