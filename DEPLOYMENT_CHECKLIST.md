# ✅ Deployment Checklist

Use this checklist to track your deployment progress.

## 📋 Pre-Deployment

- [ ] Read `DEPLOYMENT_GUIDE.md`
- [ ] Review `QUICK_REFERENCE.md`
- [ ] Have 30-45 minutes available
- [ ] Have credit card for OpenAI (no charge unless you exceed free tier)

---

## 🔑 Step 1: Get OpenAI API Key (5 minutes)

- [ ] Sign up at https://platform.openai.com/signup
- [ ] Go to https://platform.openai.com/api-keys
- [ ] Create new secret key named "DelhiPoliceBot"
- [ ] Copy and save the key (starts with `sk-...`)
- [ ] ⚠️ **Important**: You won't see this key again!

**Save your key here temporarily** (delete after deployment):
```
OPENAI_API_KEY=sk-_____________________________________________
```

---

## 🐙 Step 2: Push Code to GitHub (5 minutes)

- [ ] Create GitHub account if needed: https://github.com/signup
- [ ] Create new repository called `delhipolice-chatbot`
- [ ] Run these commands:
  ```bash
  cd /Users/nitindigraje/Documents/delhipolicechatbot
  git init
  git add .
  git commit -m "Initial commit - RAG chatbot"
  git remote add origin https://github.com/YOUR_USERNAME/delhipolice-chatbot.git
  git push -u origin main
  ```
- [ ] Verify code is visible on GitHub

**Repository URL**:
```
https://github.com/_____________________/delhipolice-chatbot
```

---

## 🗄️ Step 3: Deploy Backend (Render.com) (10 minutes)

- [ ] Sign up at https://render.com/register
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New" → "Blueprint"
- [ ] Connect GitHub account
- [ ] Select `delhipolice-chatbot` repository
- [ ] Click "Apply"
- [ ] Wait for services to create (~5 minutes)
  - [ ] PostgreSQL database created
  - [ ] Backend web service created
- [ ] Go to backend service
- [ ] Click "Environment" tab
- [ ] Add/verify these variables:
  - [ ] `OPENAI_API_KEY` = (paste your key from Step 1)
  - [ ] `ADMIN_PASSWORD` = (choose a secure password)
  - [ ] All other variables auto-filled from Blueprint
- [ ] Click "Save Changes"
- [ ] Wait for redeploy (~3 minutes)
- [ ] Service status shows "Live" (green)

**Save your backend URL**:
```
Backend URL: https://________________________________.onrender.com
Admin Password: _______________________
```

---

## ✅ Step 4: Test Backend (2 minutes)

- [ ] Open browser, go to: `https://YOUR-BACKEND-URL.onrender.com/health`
- [ ] Should see: `{"status":"healthy"}`
- [ ] Go to: `https://YOUR-BACKEND-URL.onrender.com/docs`
- [ ] Should see FastAPI Swagger UI

If tests fail:
- [ ] Check Render logs: Dashboard → Service → Logs
- [ ] Verify `OPENAI_API_KEY` is set correctly
- [ ] Wait 1-2 minutes and try again (might be starting up)

---

## 🎨 Step 5: Deploy Admin UI (Vercel) (5 minutes)

### Option A: Via CLI
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Run:
  ```bash
  cd /Users/nitindigraje/Documents/delhipolicechatbot/frontend/admin
  vercel
  ```
- [ ] Follow prompts (project name: `delhipolice-admin`)
- [ ] Set environment variable:
  ```bash
  vercel env add NEXT_PUBLIC_API_URL production
  # Enter your backend URL: https://your-backend-url.onrender.com
  ```
- [ ] Deploy: `vercel --prod`

### Option B: Via Dashboard
- [ ] Sign up at https://vercel.com/signup
- [ ] Go to https://vercel.com/dashboard
- [ ] Click "Add New" → "Project"
- [ ] Import your GitHub repo
- [ ] Settings:
  - [ ] Framework: Next.js
  - [ ] Root Directory: `frontend/admin`
  - [ ] Build Command: `npm run build`
- [ ] Add Environment Variable:
  - [ ] Key: `NEXT_PUBLIC_API_URL`
  - [ ] Value: (your backend URL)
- [ ] Click "Deploy"
- [ ] Wait for deployment (~2 minutes)

**Save your admin URL**:
```
Admin URL: https://________________________________.vercel.app
```

---

## 💬 Step 6: Deploy Chat UI (Vercel) (5 minutes)

Repeat Step 5 for chat frontend:

### Via CLI
```bash
cd /Users/nitindigraje/Documents/delhipolicechatbot/frontend/chat
vercel
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.onrender.com
vercel --prod
```

### Via Dashboard
- [ ] Same as Step 5, but Root Directory: `frontend/chat`
- [ ] Project name: `delhipolice-chat`

**Save your chat URL**:
```
Chat URL: https://________________________________.vercel.app
```

---

## 🧪 Step 7: Test Everything (5 minutes)

### Test Admin UI
- [ ] Go to your admin URL
- [ ] Login with:
  - Username: `admin`
  - Password: (from Step 3)
- [ ] Upload a test PDF document
- [ ] Wait for "Processing complete" message
- [ ] Verify document appears in list

### Test Chat UI
- [ ] Go to your chat URL
- [ ] Should see chat interface
- [ ] Type: "Hello, are you working?"
- [ ] Should get response from AI
- [ ] Ask question about your uploaded document
- [ ] Should get relevant response

---

## 🎉 Deployment Complete!

If all checkboxes above are checked, your chatbot is live!

### Your Deployment Info

**URLs** (save these!):
- Backend API: `_____________________________________`
- Admin Panel: `_____________________________________`
- Chat Interface: `_____________________________________`

**Credentials** (keep private!):
- Admin Username: `admin`
- Admin Password: `_____________________________________`
- OpenAI API Key: `sk-____________________________________`

### Share Your Chatbot
- ✅ **Public**: Share chat URL with anyone
- ⚠️ **Private**: Keep admin URL and password secret
- 🔒 **Secure**: Never share OpenAI API key

---

## 📊 Post-Deployment Tasks

- [ ] **Change default password**: 
  - Go to Render → Service → Environment
  - Update `ADMIN_PASSWORD` to something secure
  - Save and redeploy
  
- [ ] **Upload your documents**:
  - Login to admin panel
  - Upload Delhi Police documents
  - Wait for processing
  
- [ ] **Set up usage alerts**:
  - Go to https://platform.openai.com/settings/organization/limits
  - Set monthly budget cap (e.g., $10)
  - Enable email alerts
  
- [ ] **Bookmark your URLs**:
  - Save admin and chat URLs to browser
  - Share chat URL with team/users
  
- [ ] **Monitor costs**:
  - Check OpenAI usage: https://platform.openai.com/usage
  - Check Render logs for errors
  - Check Vercel analytics

---

## 🔄 Ongoing Maintenance

### Weekly
- [ ] Check OpenAI usage dashboard
- [ ] Verify chatbot is responding correctly
- [ ] Check Render logs for errors

### Monthly
- [ ] Review OpenAI costs
- [ ] Verify all services still on free tier
- [ ] Update documents if needed

### As Needed
- [ ] Update code: `git push origin main` (auto-deploys)
- [ ] Add/remove documents via admin panel
- [ ] Adjust RAG parameters in Render env vars

---

## 🆘 Troubleshooting

### Issue: Backend shows "Application failed to respond"
- [ ] Check Render logs for errors
- [ ] Verify `OPENAI_API_KEY` is set
- [ ] Redeploy manually: Dashboard → Manual Deploy

### Issue: Frontend shows "Network Error"
- [ ] Check `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Test backend health endpoint
- [ ] Verify backend is awake (visit /health)

### Issue: OpenAI API errors
- [ ] Check API key is valid: https://platform.openai.com/api-keys
- [ ] Verify billing is set up (need card on file)
- [ ] Check rate limits

### Issue: "Admin login failed"
- [ ] Verify username is `admin`
- [ ] Check password matches Render env var
- [ ] Clear browser cache and try again

### Still stuck?
- [ ] Check `QUICK_REFERENCE.md` for commands
- [ ] Review `DEPLOYMENT_GUIDE.md` for details
- [ ] Check Render logs: Dashboard → Service → Logs
- [ ] Check Vercel logs: Dashboard → Deployments → Function Logs

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `DEPLOYMENT_GUIDE.md` | Full step-by-step deployment guide |
| `QUICK_REFERENCE.md` | Commands, URLs, troubleshooting |
| `README.md` | Project overview and features |
| `.env.example` | Environment variable template |
| `render.yaml` | Render.com deployment configuration |
| `test_deployment.sh` | Local testing script |

---

## ✅ Success Criteria

You've successfully deployed when:
- ✅ Backend health check returns "healthy"
- ✅ Admin panel loads and login works
- ✅ Documents can be uploaded and processed
- ✅ Chat UI loads and responds to messages
- ✅ Chat answers questions about uploaded documents
- ✅ All services show "Live" status
- ✅ No errors in Render/Vercel logs

---

**Congratulations!** 🎉

Your Delhi Police RAG Chatbot is now live and ready to use!

**Total time**: ~35 minutes
**Total cost**: $0 initially (with free credits)
**Next step**: Upload your documents and start chatting!

---

**Date Completed**: _______________
**Deployed By**: _______________
**Notes**: _______________________________________________
