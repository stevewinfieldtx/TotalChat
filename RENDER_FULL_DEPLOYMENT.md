# Render Full Deployment Guide

## Can Render Host Everything?
**Yes!** But you need to deploy 2 separate services:
1. Backend as "Web Service"
2. Frontend as "Static Site"

## 🚀 Full Render Deployment

### Step 1: Deploy Backend (5 minutes)

1. Go to **https://render.com** and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub `TotalChat` repo
4. Configure:
   - **Name**: `totalchat-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Starter ($7/mo for no cold starts)

5. Add Environment Variables:
```env
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY
ELEVENLABS_API_KEY=sk_YOUR_KEY
RUNWARE_API_KEY=YOUR_KEY
OPENROUTER_APP_TITLE=TotalChat
OPENROUTER_HTTP_REFERER=https://your-app-name.onrender.com
```

6. Click "Create Web Service"
7. **Copy the backend URL** (e.g., `https://totalchat-backend.onrender.com`)

### Step 2: Configure Frontend

Update `frontend/.env.production` with your backend URL:
```bash
VITE_BACKEND_URL=https://totalchat-backend.onrender.com
```

Commit:
```bash
git add frontend/.env.production
git commit -m "Set Render backend URL"
git push
```

### Step 3: Deploy Frontend (5 minutes)

1. In Render, click "New +" → "Static Site"
2. Connect same GitHub repo
3. Configure:
   - **Name**: `totalchat-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variables:
```env
VITE_BACKEND_URL=https://totalchat-backend.onrender.com
```
(Use your actual backend URL from Step 1)

5. Click "Create Static Site"
6. **Copy the frontend URL** (e.g., `https://totalchat-frontend.onrender.com`)

### Step 4: Update Backend CORS

Go back to backend service:
1. Environment → Add/Edit:
```env
CORS_ORIGIN=https://totalchat-frontend.onrender.com
```
(Use your actual frontend URL from Step 3)

2. Save (this triggers a redeploy)

### Step 5: Test!
Visit your frontend URL and test the chat!

---

## 💰 Render Pricing

**Free Tier:**
- Backend: Free (with cold starts ~20-30s after 15 min idle)
- Frontend: Free
- **Total: $0/month**

**Paid (No Cold Starts):**
- Backend Starter: $7/month
- Frontend: Free
- **Total: $7/month**

---

## ⚠️ Render Limitations

1. **Cold Starts**: Free tier backend spins down after 15 min idle
2. **Manual Setup**: Need to configure 2 services separately
3. **CORS Updates**: Must update CORS when URLs change

---

## 🆚 Render vs Railway

| Feature | Railway | Render |
|---------|---------|--------|
| Services | 1 project, auto-connected | 2 services, manual connect |
| Setup | 5 minutes | 10-15 minutes |
| Cold Starts (Free) | ~5-10s | ~20-30s |
| Cost (Free) | $5 credit/mo | Truly free |
| Cost (Paid) | $10-15/mo | $7/mo |
| Best For | Simplicity | Saving money |

**Choose Render if:** You want to save money and don't mind cold starts
**Choose Railway if:** You want simplicity and faster cold starts

---

## 🎯 Render Checklist

- [ ] Deploy backend Web Service
- [ ] Copy backend URL
- [ ] Update frontend/.env.production
- [ ] Commit and push
- [ ] Deploy frontend Static Site
- [ ] Copy frontend URL
- [ ] Update backend CORS_ORIGIN
- [ ] Test the app
- [ ] 🎉 Done!
