# 📋 Quick Deployment Reference

## 🔗 Important URLs

### Development (Local)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin UI: http://localhost:3000
- Chat UI: http://localhost:3001
- PostgreSQL: localhost:5432
- ChromaDB: Embedded in backend

### Production (To be filled after deployment)
- Backend API: `https://your-backend-url.onrender.com`
- Admin UI: `https://your-admin-url.vercel.app`
- Chat UI: `https://your-chat-url.vercel.app`

---

## 🚀 Quick Start Commands

### Local Development
```bash
# Test deployment locally
./test_deployment.sh

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Reset everything (including data)
docker-compose down -v
```

### Frontend Development
```bash
# Admin UI
cd frontend/admin
npm install
npm run dev  # Runs on http://localhost:3000

# Chat UI
cd frontend/chat
npm install
npm run dev  # Runs on http://localhost:3001
```

---

## 📦 Deployment Commands

### Push to GitHub
```bash
cd /Users/nitindigraje/Documents/delhipolicechatbot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/delhipolice-chatbot.git
git push -u origin main
```

### Deploy Backend (Render)
**Option 1: Blueprint (Recommended)**
1. Go to https://dashboard.render.com/
2. New → Blueprint
3. Connect GitHub repo
4. Apply

**Option 2: Manual**
1. New → Web Service
2. Connect repo
3. Settings:
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Deploy Frontend (Vercel)
```bash
# Admin UI
cd frontend/admin
vercel
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.onrender.com
vercel --prod

# Chat UI
cd frontend/chat
vercel
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.onrender.com
vercel --prod
```

---

## 🔑 Environment Variables

### Backend (Render)
| Variable | Value | Required |
|----------|-------|----------|
| `LLM_PROVIDER` | `openai` | ✅ |
| `OPENAI_API_KEY` | `sk-...` | ✅ |
| `OPENAI_MODEL` | `gpt-4o-mini` | ✅ |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | ✅ |
| `DATABASE_URL` | Auto-filled by Render | ✅ |
| `CHROMA_URL` | `embedded` | ✅ |
| `CHROMA_PERSIST_DIR` | `/app/chroma_data` | ✅ |
| `SECRET_KEY` | Generate with `openssl rand -hex 32` | ✅ |
| `ADMIN_USERNAME` | `admin` | ✅ |
| `ADMIN_PASSWORD` | Your secure password | ✅ |
| `CHUNK_SIZE` | `1000` | Optional |
| `CHUNK_OVERLAP` | `200` | Optional |
| `TOP_K_RESULTS` | `8` | Optional |
| `CHAT_HISTORY_LIMIT` | `5` | Optional |

### Frontend (Vercel)
| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.onrender.com` | ✅ |

---

## 🧪 Testing Endpoints

### Health Check
```bash
curl https://your-backend-url.onrender.com/health
# Expected: {"status":"healthy"}
```

### Chat (No Auth Required)
```bash
curl -X POST https://your-backend-url.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "conversation_id": "test-123"
  }'
```

### Get Admin Token
```bash
curl -X POST https://your-backend-url.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'
# Copy the "access_token" from response
```

### Upload Document (Requires Token)
```bash
curl -X POST https://your-backend-url.onrender.com/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/document.pdf"
```

### List Documents
```bash
curl -X GET https://your-backend-url.onrender.com/api/documents \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Monitoring & Logs

### Render (Backend)
- Dashboard: https://dashboard.render.com/
- Logs: Service → Logs tab
- Metrics: Service → Metrics tab

### Vercel (Frontend)
- Dashboard: https://vercel.com/dashboard
- Deployments: Project → Deployments
- Function Logs: Deployment → View Function Logs

### OpenAI (API Usage)
- Usage: https://platform.openai.com/usage
- API Keys: https://platform.openai.com/api-keys
- Limits: https://platform.openai.com/settings/organization/limits

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Render logs
# Common issues:
# 1. Missing OPENAI_API_KEY
# 2. Invalid DATABASE_URL
# 3. Port binding issue (use $PORT in Render)
```

### Frontend can't connect to backend
```bash
# Check NEXT_PUBLIC_API_URL in Vercel
# Make sure it doesn't have trailing slash
# Test backend health endpoint first
```

### OpenAI errors
```bash
# Invalid API key: Generate new key
# Rate limit: Wait or add credits
# Model not found: Check OPENAI_MODEL spelling
```

### Database errors
```bash
# Check DATABASE_URL in Render
# Verify PostgreSQL service is running
# Check connection string format
```

---

## 🔄 Updating After Changes

### Backend Code Changes
```bash
git add .
git commit -m "Update backend"
git push origin main
# Render auto-deploys (if GitHub connected)
# Or: Manual Deploy in Render dashboard
```

### Frontend Code Changes
```bash
cd frontend/admin  # or frontend/chat
git add .
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys (if GitHub connected)
# Or: Run `vercel --prod` manually
```

### Environment Variable Changes
**Render**: Dashboard → Service → Environment → Edit → Save Changes → Manual Deploy
**Vercel**: Dashboard → Project → Settings → Environment Variables → Save → Redeploy

---

## 📈 Cost Optimization

### Free Tier Limits
- **Render Backend**: 750 hours/month (enough for 1 service always-on)
- **Render PostgreSQL**: 1GB storage, 97 connections
- **Vercel**: 100GB bandwidth/month, 100 deployments
- **OpenAI**: $5 free credit (3 months)

### Reduce OpenAI Costs
```bash
# In Render environment variables:
OPENAI_MODEL=gpt-3.5-turbo  # 3x cheaper than gpt-4o-mini
TOP_K_RESULTS=5              # Fewer context documents
CHUNK_SIZE=500               # Smaller chunks
CHAT_HISTORY_LIMIT=3         # Less conversation memory
```

### Monitor Usage
- Set up billing alerts in OpenAI dashboard
- Check Render metrics for database usage
- Monitor Vercel bandwidth usage

---

## 🆘 Get Help

### Check Logs
```bash
# Render
Dashboard → Service → Logs

# Vercel
Dashboard → Project → Deployments → View Function Logs

# Local
docker-compose logs -f backend
```

### Common Commands
```bash
# Reset local database
docker-compose down -v && docker-compose up -d

# Test backend health
curl http://localhost:8000/health

# Check environment variables
docker-compose exec backend env | grep -E "LLM_PROVIDER|OPENAI|CHROMA"

# Access database
docker-compose exec postgres psql -U rag -d ragdb
```

---

## 📚 Documentation

- **Full Guide**: `DEPLOYMENT_GUIDE.md`
- **Project README**: `README.md`
- **API Docs**: `https://your-backend-url.onrender.com/docs`
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **OpenAI Docs**: https://platform.openai.com/docs

---

## ✅ Pre-Deployment Checklist

- [ ] OpenAI API key obtained
- [ ] GitHub account created
- [ ] Render account created
- [ ] Vercel account created
- [ ] Code pushed to GitHub
- [ ] `.env` file configured locally
- [ ] Local testing passed (`./test_deployment.sh`)
- [ ] Admin password chosen (secure!)
- [ ] Backend deployed to Render
- [ ] Environment variables set in Render
- [ ] Backend health check passes
- [ ] Admin UI deployed to Vercel
- [ ] Chat UI deployed to Vercel
- [ ] Frontend connected to backend
- [ ] Test document uploaded
- [ ] Test chat conversation works
- [ ] URLs saved for future reference

---

**Last Updated**: December 2024
**Deployment Type**: Hybrid (Render + Vercel + OpenAI)
**Estimated Setup Time**: 30-45 minutes
**Estimated Monthly Cost**: $0-5 (after free credits)
