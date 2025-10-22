# Railway Deployment Guide - The Simple Way

## Why Railway?
Railway is **THE BEST** option for TotalChat because:
- Deploys frontend AND backend automatically
- Native WebSocket support (required for chat)
- Fast deployment (3-5 minutes total)
- One platform to manage
- $5/month free credit to start
- No cold start issues like Render

## 🚀 Quick Deploy (5 Minutes)

### Option 1: Deploy via GitHub (Easiest)

#### Step 1: Sign Up
1. Go to **https://railway.app**
2. Click "Login" → Sign in with GitHub
3. Authorize Railway to access your repositories

#### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `TotalChat` repository
4. Railway will auto-detect both services!

#### Step 3: Configure Environment Variables
Click on your project, then add these variables:

**For Backend Service:**
```env
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
ELEVENLABS_API_KEY=sk_YOUR_KEY_HERE
RUNWARE_API_KEY=YOUR_KEY_HERE
OPENROUTER_APP_TITLE=TotalChat
```

**For Frontend Service:**
Railway will auto-set `VITE_BACKEND_URL` to connect to your backend!

#### Step 4: Deploy
1. Click "Deploy"
2. Wait 3-5 minutes
3. Railway gives you a public URL
4. **Done!** 🎉

---

### Option 2: Deploy via CLI (More Control)

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Login
```bash
railway login
```
This opens a browser to authenticate.

#### Step 3: Initialize and Deploy
```bash
cd /home/user/TotalChat

# Initialize Railway project
railway init

# Deploy everything
railway up
```

#### Step 4: Add Environment Variables
```bash
# Set variables via CLI
railway variables set OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY"
railway variables set ELEVENLABS_API_KEY="sk_YOUR_KEY"
railway variables set RUNWARE_API_KEY="YOUR_KEY"
railway variables set OPENROUTER_APP_TITLE="TotalChat"
```

Or set them in the Railway dashboard (easier).

#### Step 5: Open Your App
```bash
railway open
```

---

## 📋 What Railway Does Automatically

When you deploy, Railway:
1. ✅ Detects it's a Python + Node.js app
2. ✅ Installs backend dependencies (`pip install -r backend/requirements.txt`)
3. ✅ Installs frontend dependencies (`npm install` in frontend/)
4. ✅ Builds frontend (`npm run build`)
5. ✅ Starts backend with WebSocket support
6. ✅ Serves frontend static files
7. ✅ Connects them together with internal networking
8. ✅ Provides HTTPS domain automatically
9. ✅ Sets up auto-deploy on git push

**You don't configure ANY of this - it just works!**

---

## 🔧 Configuration Files

I've created these files for optimal Railway deployment:

### `railway.toml`
Tells Railway how to run your backend.

### `nixpacks.toml`
Tells Railway how to build both frontend and backend.

These files are committed to your repo, so Railway knows exactly what to do!

---

## 💰 Pricing

### Free Tier
- $5 credit per month
- Perfect for testing and development
- ~500 hours of execution time
- Enough for moderate usage

### Hobby Plan
- $5/month + usage
- Typical cost: $10-15/month for moderate traffic
- No cold starts
- More resources

### Usage-Based Costs
Railway charges based on:
- CPU time
- Memory usage
- Network egress

For a chat app with 100-500 messages/day: ~$10-20/month total.

---

## 🔍 Monitoring Your App

### View Logs
```bash
railway logs
```

Or view in dashboard: Project → Deployments → Logs

### Check Status
```bash
railway status
```

### View Metrics
In Railway dashboard:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🐛 Troubleshooting

### Issue: "Build failed"
**Solution**: Check that `backend/requirements.txt` exists
```bash
# Verify file exists
ls -la backend/requirements.txt

# If missing, create it
cat > backend/requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.0
EOF
```

### Issue: "Cannot connect to backend"
**Solution**: Railway auto-sets VITE_BACKEND_URL, but verify:
1. In Railway dashboard, click on frontend service
2. Check Variables tab
3. Ensure `VITE_BACKEND_URL` points to backend service URL

### Issue: "CORS error"
**Solution**: Add CORS_ORIGIN variable:
```bash
railway variables set CORS_ORIGIN="https://your-app.railway.app"
```

Or set it in dashboard to your Railway app URL.

### Issue: "OpenRouter API not working"
**Solution**: Verify API key is set correctly:
```bash
railway variables
```
Check that OPENROUTER_API_KEY is present and correct.

---

## 🔄 Continuous Deployment

Railway automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update character"
git push
```

Railway detects the push and redeploys automatically (1-2 minutes).

---

## 📊 Compare All Options

| Feature | Railway | Vercel+Render |
|---------|---------|---------------|
| Platforms | 1 | 2 |
| Setup Time | 5 min | 15 min |
| WebSockets | ✅ Native | ✅ Render only |
| Auto-Deploy | ✅ Yes | ✅ Yes |
| Cold Starts | Fast (5-10s) | Slow (20-30s on Render free) |
| Free Tier | $5 credit/mo | Both free |
| Paid Cost | $10-15/mo | $7/mo (Render) |
| Complexity | Low | Medium |
| **Best For** | **Full-stack apps** | Splitting services |

**Winner for TotalChat: Railway** 🏆

---

## 🎯 Quick Start Checklist

- [ ] Sign up at railway.app
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select TotalChat repository
- [ ] Add environment variables (API keys)
- [ ] Click "Deploy"
- [ ] Wait 3-5 minutes
- [ ] Visit your Railway URL
- [ ] Test character selection and chat
- [ ] 🎉 Done!

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

## 🚀 Next Steps After Deployment

1. **Custom Domain** (optional)
   - In Railway: Settings → Domains → Add Custom Domain
   - Point your DNS to Railway's nameservers

2. **Add More Characters**
   - Add JSON files to `public/characters/`
   - Add `"llm": "model-name"` to each JSON
   - Push to GitHub
   - Railway auto-deploys!

3. **Monitor Usage**
   - Watch Railway dashboard for costs
   - Optimize API calls if needed
   - Add caching for common requests

4. **Scale Up**
   - Railway auto-scales based on traffic
   - No configuration needed!

---

## 💡 Pro Tips

1. **Use Preview Deployments**
   - Railway creates preview URLs for PRs
   - Test changes before merging to main

2. **Environment Switching**
   - Create separate Railway projects for dev/staging/prod
   - Each has its own environment variables

3. **Database Integration**
   - Railway offers PostgreSQL, Redis, MongoDB
   - One-click add-on, no external service needed

4. **Cost Optimization**
   - Railway shows real-time costs
   - Set spending limits in Settings
   - Get alerts at spending thresholds

---

That's it! Railway is designed for apps exactly like TotalChat. Deploy and enjoy! 🎉
