# Vercel + Render Deployment Guide

## Quick Overview
- **Frontend**: Vercel (React/Vite)
- **Backend**: Render (FastAPI/WebSockets)

## Step 1: Deploy Backend to Render

### 1.1 Sign up for Render
Go to https://render.com and sign up (free tier available)

### 1.2 Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `totalchat-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or Starter for no cold starts)

### 1.3 Add Environment Variables
In Render dashboard, add:
```
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
ELEVENLABS_API_KEY=sk_YOUR_KEY_HERE
RUNWARE_API_KEY=YOUR_KEY_HERE
OPENROUTER_HTTP_REFERER=https://your-app.vercel.app
OPENROUTER_APP_TITLE=TotalChat
CORS_ORIGIN=https://your-app.vercel.app
```

### 1.4 Deploy
Click "Create Web Service" and wait for deployment (3-5 minutes)

### 1.5 Copy Your Backend URL
After deployment, copy the URL (e.g., `https://totalchat-backend.onrender.com`)

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Update Backend URL
1. Edit `frontend/.env.production`:
   ```bash
   VITE_BACKEND_URL=https://totalchat-backend.onrender.com
   ```
   (Use your actual Render URL from Step 1.5)

2. Commit the change:
   ```bash
   git add frontend/.env.production
   git commit -m "Add production backend URL"
   git push
   ```

### 2.2 Sign up for Vercel
Go to https://vercel.com and sign up with GitHub

### 2.3 Import Project
1. Click "Add New..." → "Project"
2. Import your `TotalChat` repository
3. Vercel will auto-detect Vite

### 2.4 Configure Build Settings
Vercel should auto-detect, but verify:
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 2.5 Add Environment Variables (Optional)
If you want to add any frontend env vars:
```
VITE_DEFAULT_MODEL=x-ai/grok-4-fast
```

### 2.6 Deploy
Click "Deploy" and wait (1-2 minutes)

### 2.7 Get Your Frontend URL
Copy the Vercel URL (e.g., `https://totalchat-abc123.vercel.app`)

---

## Step 3: Update CORS Settings

### 3.1 Update Backend CORS
Go back to Render dashboard:
1. Go to your backend service
2. Environment → Edit `CORS_ORIGIN`
3. Set it to your Vercel URL: `https://totalchat-abc123.vercel.app`
4. Save changes (this will redeploy)

---

## Step 4: Test Your Deployment

1. Visit your Vercel URL
2. You should see the TotalChat interface
3. Try selecting characters and starting a chat
4. Check browser console for any errors

### Troubleshooting

**Issue**: "Failed to connect to WebSocket"
- Check that CORS_ORIGIN in Render matches your Vercel URL
- Ensure backend is running (Render free tier has cold starts)

**Issue**: "Network error"
- Check that VITE_BACKEND_URL in frontend/.env.production is correct
- Make sure it starts with `https://` not `http://`

**Issue**: Backend is slow on first load
- This is normal on Render's free tier (cold starts)
- Upgrade to Starter plan ($7/month) to eliminate cold starts
- Or use Railway for faster cold starts

---

## Alternative: Use Railway for Everything

If you want simpler deployment, use Railway for both:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

Railway auto-detects both services and costs ~$10-15/month.

---

## Cost Comparison

### Vercel + Render (Free Tier)
- **Cost**: $0/month
- **Pros**: Great for testing, generous limits
- **Cons**: Backend has cold starts (20-30s delay after inactivity)

### Vercel + Render (Paid)
- **Cost**: ~$7/month (Vercel free + Render Starter)
- **Pros**: No cold starts, always fast
- **Cons**: Need to manage 2 platforms

### Railway (All-in-One)
- **Cost**: ~$10-15/month
- **Pros**: Simplest, one platform, faster cold starts
- **Cons**: Slightly more expensive

---

## Environment Variables Summary

### Backend (Render)
```env
OPENROUTER_API_KEY=sk-or-v1-...
ELEVENLABS_API_KEY=sk_...
RUNWARE_API_KEY=...
OPENROUTER_HTTP_REFERER=https://your-app.vercel.app
OPENROUTER_APP_TITLE=TotalChat
CORS_ORIGIN=https://your-app.vercel.app
```

### Frontend (Vercel)
```env
VITE_BACKEND_URL=https://your-backend.onrender.com
```

---

## Next Steps

1. ✅ Deploy backend to Render (get URL)
2. ✅ Update frontend/.env.production with backend URL
3. ✅ Deploy frontend to Vercel (get URL)
4. ✅ Update backend CORS with frontend URL
5. 🎉 Test and enjoy!

---

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Need help? Check DEPLOYMENT.md for more options
