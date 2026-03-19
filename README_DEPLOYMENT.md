# Portfolio Optimization AI - Deployment Guide

## 🏗️ Architecture Overview

```
Frontend (Vercel) → Backend API (Render/Railway)
     ↓                        ↓
   Static HTML              FastAPI + ML Models
   (~50KB)                  (~200MB)
```

## 🚀 Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import `frontend` folder from your GitHub
4. Settings:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
5. Click "Deploy"

### Step 2: Environment Variables
In Vercel dashboard → Settings → Environment Variables:
```
API_BASE_URL=https://your-backend-url.onrender.com
```

### Step 3: Verify Deployment
Your frontend will be available at:
`https://portfolio-optimization-ai-frontend.vercel.app`

---

## 🚀 Backend Deployment (Render)

### Step 1: Deploy to Render
1. Go to [render.com](https://render.com)
2. Click "New Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Name**: portfolio-optimization-api
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. Click "Create Web Service"

### Step 2: Environment Variables
In Render dashboard → Environment:
```
PYTHON_VERSION=3.11
PORT=8000
```

### Step 3: Verify Deployment
Your API will be available at:
`https://portfolio-optimization-api.onrender.com`

---

## 🔧 Alternative: Railway Deployment

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Deploy from GitHub
4. Select `backend` folder
5. Railway will auto-detect Python and deploy

### Step 2: Configuration
Add environment variables in Railway dashboard:
```
PYTHON_VERSION=3.11
PORT=8000
```

---

## 📱 Testing the Full Stack

### 1. Test Backend API
```bash
curl https://your-backend-url.onrender.com/health
```

### 2. Test Frontend
Visit your Vercel URL and try optimizing a portfolio.

### 3. Test Integration
- Enter tickers: AAPL, MSFT, GOOG, AMZN
- Click "Optimize Portfolio"
- Should see results from backend API

---

## 🎯 Final URLs Structure

```
Frontend: https://portfolio-optimization-ai-frontend.vercel.app
Backend:  https://portfolio-optimization-api.onrender.com
API Docs: https://portfolio-optimization-api.onrender.com/docs
```

---

## 🔥 LinkedIn Post Update

Once deployed, update your LinkedIn post with the working frontend URL:

```
🚀 Live Dashboard: https://portfolio-optimization-ai-frontend.vercel.app/
```

---

## 📊 Build Sizes

- **Frontend**: ~50KB (well under 500MB limit)
- **Backend**: ~200MB (ML dependencies only)
- **Total**: ~250MB (efficient separation)

---

## 🛠️ Troubleshooting

### Frontend Issues
- CORS errors? Check backend CORS settings
- API not responding? Verify backend URL in environment variables

### Backend Issues
- Build fails? Check Python version and dependencies
- Slow response? ML models take time to load (cold start)

### Integration Issues
- 404 errors? Check API endpoints
- Timeout errors? Increase timeout in frontend API client

---

## 🎉 Success Metrics

✅ Frontend deploys in < 2 minutes  
✅ Backend deploys in < 5 minutes  
✅ Full stack working  
✅ Vercel build size < 500MB  
✅ LinkedIn demo link works for everyone
