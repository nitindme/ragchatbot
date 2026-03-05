# 🚀 Deployment Guide - Free Tier Hosting

This guide walks you through deploying the Delhi Police RAG Chatbot to free cloud platforms.

## 📋 Prerequisites

1. **Accounts needed** (all free):
   - [OpenAI Account](https://platform.openai.com/signup) - For API access
   - [Render.com Account](https://render.com/register) - For backend + database
   - [Vercel Account](https://vercel.com/signup) - For frontend applications
   - [GitHub Account](https://github.com/signup) - For code hosting (optional but recommended)

2. **Tools needed**:
   - Git (already installed on macOS)
   - Node.js 18+ (for local frontend testing)

## 🔑 Step 1: Get OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Name it "DelhiPoliceBot" or similar
4. **Copy the key immediately** (you won't see it again!)
5. Save it somewhere safe - you'll need it in Step 3

**Free Tier**: $5 free credit for first 3 months, then pay-as-you-go (~$0.002 per 1K tokens)

---

## 🗄️ Step 2: Deploy Database (Render.com)

### Option A: Using Blueprint (Recommended)

1. **Push code to GitHub** (if not already done):
   ```bash
   cd /Users/nitindigraje/Documents/delhipolicechatbot
   git init
   git add .
   git commit -m "Initial commit - RAG chatbot"
   # Create a new repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/delhipolice-chatbot.git
   git push -u origin main
   ```

2. **Deploy via Blueprint**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select the `delhipolice-chatbot` repository
   - Click "Apply"
   
3. **Wait for services to create** (~5 minutes):
   - ✅ PostgreSQL database
   - ✅ Backend web service

### Option B: Manual Setup (Alternative)

If Blueprint doesn't work, create services manually:

**2a. Create PostgreSQL Database:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "PostgreSQL"
3. Settings:
   - Name: `delhipolice-postgres`
   - Database: `ragdb`
   - User: `rag`
   - Region: Oregon (Free)
   - Plan: **Free**
4. Click "Create Database"
5. **Copy the "Internal Database URL"** (starts with `postgresql://`)

**2b. Create Backend Web Service:**
1. Click "New" → "Web Service"
2. Connect your GitHub repository (or use "Public Git repository")
3. Settings:
   - Name: `delhipolice-backend`
   - Region: Oregon (Free)
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**
4. Click "Create Web Service" (don't wait for it to deploy yet)

---

## 🔧 Step 3: Configure Environment Variables (Render)

1. Go to your `delhipolice-backend` service
2. Click "Environment" in left sidebar
3. Add the following variables:

| Key | Value | Notes |
|-----|-------|-------|
| `LLM_PROVIDER` | `openai` | Use OpenAI instead of Ollama |
| `OPENAI_API_KEY` | `sk-...` | Your API key from Step 1 |
| `OPENAI_MODEL` | `gpt-4o-mini` | Cheaper model (~$0.15/1M tokens) |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | Embedding model |
| `DATABASE_URL` | `postgresql://...` | Auto-filled if using Blueprint |
| `CHROMA_URL` | `embedded` | Use embedded ChromaDB |
| `CHROMA_PERSIST_DIR` | `/app/chroma_data` | Persistent storage |
| `SECRET_KEY` | (generate random) | Use: `openssl rand -hex 32` |
| `ADMIN_USERNAME` | `admin` | Admin login username |
| `ADMIN_PASSWORD` | `your-secure-password` | **Change this!** |
| `CHUNK_SIZE` | `1000` | RAG chunk size |
| `CHUNK_OVERLAP` | `200` | RAG chunk overlap |
| `TOP_K_RESULTS` | `8` | Number of context docs |
| `CHAT_HISTORY_LIMIT` | `5` | Conversation memory |

4. Click "Save Changes"
5. Service will automatically redeploy (~3-5 minutes)

---

## ✅ Step 4: Verify Backend Deployment

1. Wait for deployment to complete (status turns green)
2. Copy your backend URL (e.g., `https://delhipolice-backend.onrender.com`)
3. Test health endpoint in browser:
   ```
   https://your-backend-url.onrender.com/health
   ```
   Should return: `{"status": "healthy"}`

4. Test API docs:
   ```
   https://your-backend-url.onrender.com/docs
   ```
   Should show FastAPI Swagger UI

---

## 🎨 Step 5: Deploy Admin UI (Vercel)

1. **Install Vercel CLI** (optional, or use web UI):
   ```bash
   npm install -g vercel
   ```

2. **Deploy Admin Frontend**:
   ```bash
   cd /Users/nitindigraje/Documents/delhipolicechatbot/frontend/admin
   vercel
   ```
   
   Follow prompts:
   - Link to existing project? **No**
   - Project name: `delhipolice-admin`
   - Which directory is your code? **.**
   - Want to override settings? **No**

3. **Set Environment Variable**:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   ```
   Enter your backend URL: `https://your-backend-url.onrender.com`

4. **Deploy to production**:
   ```bash
   vercel --prod
   ```

5. **Save the URL** (e.g., `https://delhipolice-admin.vercel.app`)

### Alternative: Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Settings:
   - Framework Preset: **Next.js**
   - Root Directory: `frontend/admin`
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Environment Variables:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend-url.onrender.com`
6. Click "Deploy"

---

## 💬 Step 6: Deploy Chat UI (Vercel)

Repeat Step 5 for the chat frontend:

**Via CLI**:
```bash
cd /Users/nitindigraje/Documents/delhipolicechatbot/frontend/chat
vercel
# Follow prompts (name: delhipolice-chat)
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.onrender.com
vercel --prod
```

**Via Dashboard**:
- Same as Step 5, but use Root Directory: `frontend/chat`

---

## 🧪 Step 7: Test Your Deployment

### Test Admin UI

1. Go to `https://your-admin-url.vercel.app`
2. Login with your admin credentials (from Step 3)
3. Upload a test PDF document
4. Verify it processes successfully

### Test Chat UI

1. Go to `https://your-chat-url.vercel.app`
2. Start a conversation
3. Ask questions about your uploaded document
4. Verify responses are relevant

---

## 📊 Cost Breakdown (Free Tier Limits)

| Service | Free Tier | Limit | What Happens After |
|---------|-----------|-------|-------------------|
| **Render Backend** | 750 hours/month | Sleeps after 15 min inactivity | Takes 30-60s to wake up |
| **Render PostgreSQL** | Permanent | 1GB storage, 97 connections | Upgrade to paid ($7/month) |
| **Vercel** | Permanent | 100GB bandwidth/month | Upgrade to Pro ($20/month) |
| **OpenAI** | $5 credit (3 months) | ~2,500 requests | Pay-as-you-go ($0.002/1K tokens) |

**Expected monthly cost after free credits**: $0-5 for low traffic

---

## 🛠️ Common Issues & Fixes

### Issue 1: Backend shows "Application failed to respond"

**Fix**: Check logs in Render dashboard
- Missing `OPENAI_API_KEY`? Add it in Environment tab
- Database connection error? Verify `DATABASE_URL` is set
- ChromaDB error? Ensure `CHROMA_URL=embedded` and `CHROMA_PERSIST_DIR=/app/chroma_data`

### Issue 2: Frontend shows "Network Error"

**Fix**: CORS issue
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel environment variables
- Check backend is awake (visit `/health` endpoint)
- Ensure backend URL doesn't have trailing slash

### Issue 3: OpenAI API Error "Incorrect API key"

**Fix**: 
- Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
- Create new key
- Update in Render environment variables
- Redeploy backend

### Issue 4: "429 Rate Limit Exceeded" from OpenAI

**Fix**:
- Free tier has rate limits (3 requests/min)
- Wait a minute and try again
- Consider adding credits to your OpenAI account

### Issue 5: Backend sleeping (slow first request)

**Expected behavior** on Render free tier:
- Backend sleeps after 15 minutes of inactivity
- First request takes 30-60 seconds to wake up
- Subsequent requests are instant
- **Fix**: Upgrade to paid plan ($7/month) for always-on

---

## 🔄 Updating Your Deployment

### Update Backend
```bash
# Make changes to code
git add .
git commit -m "Update backend"
git push origin main
# Render auto-deploys on push (if connected to GitHub)
```

Or manually redeploy in Render dashboard:
- Go to service → "Manual Deploy" → "Deploy latest commit"

### Update Frontend
```bash
cd frontend/admin  # or frontend/chat
vercel --prod
# Vercel auto-deploys on push if connected to GitHub
```

---

## 📚 Next Steps

1. **Secure your admin panel**:
   - Change `ADMIN_PASSWORD` to a strong password
   - Consider adding rate limiting
   - Enable HTTPS only (already default on Vercel/Render)

2. **Upload your documents**:
   - Login to admin panel
   - Upload Delhi Police documents
   - Test queries in chat UI

3. **Monitor usage**:
   - OpenAI: [Usage Dashboard](https://platform.openai.com/usage)
   - Render: Check logs for errors
   - Vercel: [Analytics](https://vercel.com/docs/concepts/analytics)

4. **Optimize costs**:
   - Use `gpt-3.5-turbo` instead of `gpt-4o-mini` (3x cheaper)
   - Reduce `TOP_K_RESULTS` to 5 (less tokens per query)
   - Set up usage alerts in OpenAI dashboard

---

## 🆘 Support

If you encounter issues:
1. Check Render logs: Dashboard → Service → Logs
2. Check Vercel logs: Dashboard → Project → Deployments → View Function Logs
3. Test backend directly: `curl https://your-backend-url.onrender.com/health`
4. Verify environment variables are set correctly

---

## 🎉 Success!

Your RAG chatbot is now live! Share these URLs:
- **Admin Panel**: `https://your-admin-url.vercel.app` (keep private)
- **Chat Interface**: `https://your-chat-url.vercel.app` (share publicly)

**Total setup time**: 30-45 minutes
**Total cost**: $0 initially (with free credits)
