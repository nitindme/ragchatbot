# RAG Chatbot with Ollama / OpenAI

A production-ready RAG (Retrieval-Augmented Generation) chatbot with admin document management, SHA256 deduplication, conversation history, and flexible LLM provider support (Ollama or OpenAI).

## 🚀 **NEW: Cloud Deployment Ready!**

This project now supports deployment to **free cloud hosting**:
- ☁️ **Render.com** (Backend + PostgreSQL)
- ⚡ **Vercel** (Admin + Chat UIs)
- 🤖 **OpenAI API** (GPT-4o-mini + Embeddings)

**Total cost**: $0 initially, $0-5/month after free credits

👉 **[See Deployment Guide](DEPLOYMENT_GUIDE.md)** for step-by-step instructions  
👉 **[Quick Reference](QUICK_REFERENCE.md)** for commands and troubleshooting  
👉 **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** for interactive setup tracking

## 🏗️ Architecture

```
┌────────────┐        ┌──────────────┐
│   Admin UI │──upload│  Backend API │
└────────────┘        │  (FastAPI)   │
                      └──────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌──────────┐  ┌────────────┐  ┌──────────┐
        │PostgreSQL│  │ Chroma DB  │  │ Ollama   │
        │ metadata │  │ embeddings │  │ LLM + emb│
        └──────────┘  └────────────┘  └──────────┘
                             │
                        ┌────▼─────┐
                        │ Chat UI  │ (Public)
                        └──────────┘
```

## ✨ Features

### Core Features
- **SHA256 Deduplication**: Prevents duplicate document embeddings
- **Chroma Cleanup**: Automatic embedding deletion when documents are removed
- **Conversation History**: Full chat history stored in PostgreSQL
- **RAG with Context**: Combines retrieved context + chat history for responses
- **JWT Authentication**: Secure admin-only document management
- **File Validation**: Size limits and MIME type checking
- **🆕 Flexible LLM Provider**: Switch between Ollama (local) or OpenAI (cloud)
- **🆕 Cloud Deployment**: One-click deployment to free hosting platforms

### Tech Stack
- **Backend**: FastAPI, LangChain, SQLAlchemy
- **Vector Store**: ChromaDB (HTTP or embedded mode)
- **LLM**: 
  - **Local**: Ollama (llama3.2 + nomic-embed-text)
  - **Cloud**: OpenAI (gpt-4o-mini + text-embedding-3-small)
- **Database**: PostgreSQL
- **Frontend**: Next.js/React
- **Infrastructure**: Docker Compose

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin.py          # Admin document management
│   │   │   ├── auth.py           # JWT authentication
│   │   │   └── chat.py           # Public chat endpoints
│   │   ├── core/
│   │   │   ├── config.py         # Configuration
│   │   │   ├── database.py       # Database connection
│   │   │   └── security.py       # JWT & password hashing
│   │   ├── models/
│   │   │   └── models.py         # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── document_service.py  # Document processing
│   │   │   └── chat_service.py      # RAG chat logic
│   │   └── main.py               # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── admin/                    # Admin UI (Next.js)
│   └── chat/                     # Public Chat UI (Next.js)
├── database/
│   └── schema.sql                # PostgreSQL schema
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Option 1: Local Development (Ollama)

#### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (for Ollama models)

#### Steps

```bash
# 1. Clone and setup
cd delhipolicechatbot
cp .env.example .env
# Edit .env: Set LLM_PROVIDER=ollama

# 2. Start services
docker-compose up -d

# 3. Download Ollama models
docker exec -it rag-ollama ollama pull llama3.2:1b
docker exec -it rag-ollama ollama pull nomic-embed-text

# 4. Test the API
curl http://localhost:8000/health
```

### Option 2: Local Development (OpenAI)

#### Prerequisites
- Docker & Docker Compose
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

#### Steps

```bash
# 1. Clone and setup
cd delhipolicechatbot
cp .env.example .env
# Edit .env: 
#   LLM_PROVIDER=openai
#   OPENAI_API_KEY=sk-your-key-here

# 2. Start services (without Ollama)
docker-compose up -d postgres chroma backend

# 3. Test the API
curl http://localhost:8000/health
```

### Option 3: Cloud Deployment (Recommended for Production)

**Deploy to free cloud hosting in ~30 minutes!**

```bash
# 1. Test locally first
./test_deployment.sh

# 2. Follow the deployment guide
# See DEPLOYMENT_GUIDE.md for detailed instructions
```

**Quick Deploy Links:**
- 📖 [Full Deployment Guide](DEPLOYMENT_GUIDE.md) - Step-by-step with screenshots
- 📋 [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Interactive checklist
- 🔧 [Quick Reference](QUICK_REFERENCE.md) - Commands and troubleshooting

**What you'll need:**
- OpenAI API key ($5 free credit)
- GitHub account (free)
- Render.com account (free tier)
- Vercel account (free tier)

**Result:** Your chatbot live at:
- Backend: `https://your-app.onrender.com`
- Admin: `https://your-admin.vercel.app`
- Chat: `https://your-chat.vercel.app`

---

## 🌐 Access Points

### Local Development
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Admin UI**: http://localhost:3000 (run `cd frontend/admin && npm install && npm run dev`)
- **Chat UI**: http://localhost:3001 (run `cd frontend/chat && npm install && npm run dev`)

### Production (After Deployment)
- **Backend API**: Your Render.com URL
- **Admin Panel**: Your Vercel admin URL (keep private!)
- **Chat Interface**: Your Vercel chat URL (share publicly)

## 📖 API Usage

### Authentication

```bash
# Login (Basic Auth)
curl -X POST http://localhost:8001/auth/login \
  -u admin:admin123

# Response: {"access_token": "...", "token_type": "bearer"}
```

### Upload Document (Admin Only)

```bash
curl -X POST http://localhost:8001/admin/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### List Documents

```bash
curl -X GET http://localhost:8001/admin/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete Document

```bash
curl -X DELETE http://localhost:8001/admin/documents/{document_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Start Chat Session (Public)

```bash
curl -X POST http://localhost:8001/chat/start
# Response: {"session_id": "..."}
```

### Send Message

```bash
curl -X POST http://localhost:8001/chat/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?"}'
```

### Get Chat History

```bash
curl -X GET http://localhost:8001/chat/{session_id}/history
```

### Session Management (New!)

```bash
# List all sessions
curl -X GET http://localhost:8001/chat/sessions

# Delete a session
curl -X DELETE http://localhost:8001/chat/{session_id}
```

### Streaming Response (New!)

```bash
# Send message with streaming response
curl -X POST http://localhost:8001/chat/{session_id}/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the document"}' \
  --no-buffer
```

## 🎨 Frontend UIs

### Admin UI (Port 3000)

Features:
- ✅ JWT-based login
- ✅ Document upload with drag-and-drop
- ✅ Document list with delete
- ✅ Duplicate detection
- ✅ File validation
- ✅ Responsive design

### Chat UI (Port 3001)

Features:
- ✅ ChatGPT-style interface
- ✅ Real-time messaging
- ✅ Message history
- ✅ Auto-scroll
- ✅ Typing indicators
- ✅ Responsive design

## 🗄️ Database Schema

### documents
```sql
id           UUID PRIMARY KEY
filename     VARCHAR(255)
content_hash VARCHAR(64) UNIQUE  -- SHA256 for deduplication
created_at   TIMESTAMP
```

### chat_sessions
```sql
id         UUID PRIMARY KEY
created_at TIMESTAMP
```

### chat_messages
```sql
id         UUID PRIMARY KEY
session_id UUID FOREIGN KEY
role       VARCHAR(20)  -- 'user' or 'assistant'
message    TEXT
created_at TIMESTAMP
```

## 🔧 Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://rag:rag@postgres:5432/ragdb

# Ollama
OLLAMA_LLM_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text

# JWT
SECRET_KEY=generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials (CHANGE IN PRODUCTION!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## 🧪 Development

### Backend Only

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Tests

```bash
# TODO: Add tests
pytest
```

## 🔐 Security Notes

### Production Checklist
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change admin credentials
- [ ] Configure CORS properly
- [ ] Use HTTPS
- [ ] Add rate limiting
- [ ] Implement proper user management
- [ ] Set up monitoring

## 📊 RAG Flow

### Document Upload
```
1. Upload file → 2. Compute SHA256 → 3. Check duplicates
    ↓
4. Extract text → 5. Chunk text → 6. Generate embeddings
    ↓
7. Store in ChromaDB with document_id metadata
```

### Chat Response
```
1. User question → 2. Embed question → 3. Similarity search (ChromaDB)
    ↓
4. Retrieve top K chunks → 5. Format prompt (context + history + question)
    ↓
6. Ollama generates answer → 7. Store Q&A in PostgreSQL
```

## 🛠️ Troubleshooting

### Ollama models not loading
```bash
docker exec -it rag-ollama ollama list
docker exec -it rag-ollama ollama pull llama3
```

### Database connection issues
```bash
docker logs rag-postgres
docker exec -it rag-postgres psql -U rag -d ragdb
```

### ChromaDB not responding
```bash
docker logs rag-chroma
docker restart rag-chroma
```

## 📝 TODO

- [x] Add frontend UIs (Admin & Chat)
- [x] Implement conversation session management
- [x] Add streaming responses
- [x] Add API rate limiting
- [ ] Add document preview in admin UI
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Add CI/CD pipeline
- [ ] Add unit and integration tests

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue first to discuss changes.

---

**Built with ❤️ using Ollama, FastAPI, and LangChain**
