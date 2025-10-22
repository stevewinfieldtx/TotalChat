# TotalChat Deployment Guide

## Overview
TotalChat is a full-stack application with a React frontend and FastAPI backend that allows users to chat with AI characters powered by OpenRouter LLMs.

## Architecture
- **Frontend**: React + Vite (Static files)
- **Backend**: FastAPI + WebSockets (Python)
- **APIs**: OpenRouter for LLMs, ElevenLabs for voice, Runware for images

## Hosting Recommendations

### 🏆 **Recommended: Railway** (Best for Full-Stack Apps)

**Pros:**
- Easiest deployment for full-stack apps
- Automatic detection of frontend and backend
- Built-in database support if needed
- Generous free tier ($5/month credit)
- WebSocket support out of the box
- Environment variable management
- Auto-scaling

**Cons:**
- Can be more expensive at scale compared to others
- Less customization than traditional VPS

**Deployment Steps:**
1. Connect your GitHub repository
2. Railway will auto-detect both services
3. Configure environment variables in the dashboard
4. Deploy with one click

**Configuration:**
Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn backend.server:app --host 0.0.0.0 --port $PORT"
```

---

### ⚡ **Alternative: Vercel (Frontend) + Render (Backend)**

#### Vercel for Frontend
**Pros:**
- Best-in-class static hosting
- Automatic deployments from Git
- Global CDN
- Free tier is generous
- Built for React/Vite apps

**Cons:**
- Backend support is limited (serverless functions only)
- No WebSocket support on free tier

**Deployment Steps:**
1. Connect GitHub repo
2. Set root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Deploy

#### Render for Backend
**Pros:**
- Native Python support
- WebSocket support
- Free tier available
- PostgreSQL database included
- Auto-deploy from Git

**Cons:**
- Free tier spins down after inactivity (cold starts)
- Slower than paid tiers

**Deployment Steps:**
1. Create new Web Service
2. Connect GitHub repo
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

---

### 🐳 **For Advanced Users: Docker + Railway/Render**

Use the included Docker setup for consistent deployments:

```dockerfile
# Dockerfile for backend
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Environment Variables

### Backend (.env in backend/)
```bash
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_HTTP_REFERER=https://yourdomain.com
OPENROUTER_APP_TITLE=TotalChat
CORS_ORIGIN=https://your-frontend-url.com
ELEVENLABS_API_KEY=your_elevenlabs_key
RUNWARE_API_KEY=your_runware_key
```

### Frontend (.env in frontend/)
```bash
VITE_BACKEND_URL=https://your-backend-url.com
VITE_OPENROUTER_API_KEY=your_key
VITE_DEFAULT_MODEL=x-ai/grok-4-fast
```

---

## Character JSON Format

Characters should be placed in `public/characters/{folder_name}/{character_id}.json`

**Important:** Add an `llm` field to specify which model to use:

```json
{
  "llm": "anthropic/claude-3.5-sonnet",
  "metadata": {
    "character_name": "Example Character",
    "version": "1.0"
  },
  "core_identity": {
    "name": "Character Name",
    "profession": "Character Title"
  },
  "psychological_profile": {
    "dominant_traits": ["trait1", "trait2"]
  }
}
```

**Supported LLM values:**
- `anthropic/claude-3.5-sonnet`
- `anthropic/claude-3-opus`
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `x-ai/grok-4-fast` (default)
- `x-ai/grok-2`
- `google/gemini-pro-1.5`
- Any OpenRouter model ID

If no `llm` field is present, the system defaults to `x-ai/grok-4-fast`.

---

## Pre-Deployment Checklist

### 1. Update CORS Origins
In `backend/server.py`, update:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:5173",  # Keep for local dev
    ],
    ...
)
```

### 2. Test Locally
```bash
# Terminal 1: Start backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

### 3. Create requirements.txt (if not exists)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.0
```

### 4. Build Frontend
```bash
cd frontend
npm run build
# Test production build
npm run preview
```

---

## Post-Deployment

### 1. Test WebSocket Connection
Use browser console:
```javascript
const ws = new WebSocket('wss://your-backend.com/ws/test123');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
```

### 2. Monitor Logs
- **Railway**: Check logs in dashboard
- **Render**: View logs in service details
- **Vercel**: Function logs in dashboard

### 3. Set up Error Monitoring
Consider integrating:
- Sentry for error tracking
- LogRocket for session replay
- DataDog for performance monitoring

---

## Cost Estimates

### Railway (Full Stack)
- Free tier: $5/month credit
- Hobby: $5/month + usage
- Estimated: $10-20/month for moderate traffic

### Vercel (Frontend) + Render (Backend)
- Vercel: Free tier sufficient for most use cases
- Render: Free tier (with cold starts) or $7/month
- Estimated: $0-7/month (free) or $7-15/month (paid)

### Scaling Considerations
- OpenRouter API costs based on tokens used
- ElevenLabs/Runware based on usage
- Add caching to reduce API calls
- Consider Redis for session management at scale

---

## Recommended Choice

**For your use case, I recommend Railway:**

1. **Simplicity**: Single platform for both frontend and backend
2. **WebSockets**: Native support without extra configuration
3. **Development Speed**: Fastest time to production
4. **Scaling**: Automatic scaling as you grow
5. **Cost**: Predictable pricing

**Deploy to Railway in 3 steps:**
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and initialize
railway login
railway init

# 3. Deploy
railway up
```

Railway will auto-detect your services and deploy them. Then add your environment variables in the dashboard.

---

## Support

For issues or questions:
- Check Railway/Render/Vercel documentation
- OpenRouter API docs: https://openrouter.ai/docs
- Create an issue in the repository

Good luck with your deployment! 🚀
