# Animal Recognizer - Deployment Guide

This guide covers deploying the Animal Recognizer frontend to **Vercel** and backend to **Render**.

## Architecture

- **Frontend**: Next.js (TypeScript) → Vercel
- **Backend**: FastAPI (Python) → Render
- **Communication**: HTTP POST to `/predict` endpoint
- **Environment**: Uses `NEXT_PUBLIC_API_URL` to know backend location

---

## Local Development

### 1. Backend (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
# or: uvicorn main:app --reload --port 8000
```

Server runs at `http://localhost:8000`  
- Health check: `GET http://localhost:8000/`
- Predict: `POST http://localhost:8000/predict` (multipart/form-data with `file`)

### 2. Frontend (Next.js)

```powershell
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`

The frontend's `.env.local` is already configured to call `http://localhost:8000`.

---

## Deployment to Render + Vercel

### Build & Test Docker Image Locally (Optional)

Before deploying to Render, test the Docker image locally:

```powershell
cd backend

# Build the image
docker build -t animal-recognizer-api:latest .

# Run the container
docker run -p 8000:8000 animal-recognizer-api:latest

# Test it
curl http://localhost:8000/
```

The image will be ~1.5GB (includes TensorFlow). This is normal.

---

### Step 1: Deploy Backend to Render

**Option A: Using Docker (Recommended)**

1. **Create Render Account** → https://render.com
2. **Push your code to GitHub**
3. **New Web Service** → Select your repository
4. **Settings**:
   - **Name**: `animal-recognizer-api`
   - **Environment**: Docker
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Start Command**: Leave empty (Dockerfile CMD runs automatically)
   - **Root Directory**: `backend`
5. **Deploy** → Copy the deployed URL (e.g., `https://animal-recognizer-api.onrender.com`)

**Test the backend**:
```bash
curl https://animal-recognizer-api.onrender.com/
```

---

**Option B: Native Python (No Docker)**

1. **Create Render Account** → https://render.com
2. **Push your code to GitHub**
3. **New Web Service** → Select your repository
4. **Settings**:
   - **Name**: `animal-recognizer-api`
   - **Environment**: Python 3.10
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
5. **Deploy** → Copy the deployed URL (e.g., `https://animal-recognizer-api.onrender.com`)

**Test the backend**:
```bash
curl https://animal-recognizer-api.onrender.com/
```

---

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account** → https://vercel.com
2. **Import Project** → Select your GitHub repo
3. **Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
4. **Environment Variables**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://animal-recognizer-api.onrender.com` (the Render backend URL from Step 1)
5. **Deploy** → App will be live at `https://your-project.vercel.app`

---

## Verify Deployment

1. Open frontend at `https://your-project.vercel.app`
2. Upload an animal image
3. Check browser DevTools (Network tab) to see POST to `NEXT_PUBLIC_API_URL/predict`
4. Verify prediction appears without errors

---

## Environment Variables Summary

| Service | Variable | Dev Value | Prod Value |
|---------|----------|-----------|------------|
| Frontend | `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | `https://animal-recognizer-api.onrender.com` |
| Backend | (none required) | - | - |

**Note**: `NEXT_PUBLIC_` prefix means the variable is baked into the frontend JavaScript bundle at build time.

---

## Troubleshooting

### CORS Errors
- Backend `main.py` allows origins: `localhost:3000`, `*.vercel.app`
- If needed, update the `origins` list in `main.py` and redeploy

### Backend Returning "Unknown Error"
- Check Render logs: Dashboard → Service → Logs
- Ensure FastAPI is running: `curl https://your-backend.onrender.com/`
- Verify `src/models/animal_model.h5` and `src/utils/labels.json` exist

### Model Not Found
- Backend expects model at `<repo-root>/src/models/animal_model.h5`
- Verify the file exists in version control (or upload separately)

### "Mock Predictor" Mode
- If heavy dependencies (TensorFlow, Pillow) aren't installed, backend runs in "mock" mode
- Predictions still work but return hardcoded values (for testing)
- To use real model, ensure Python 3.10 + all deps from `requirements.txt` are installed

---

## Optional: Custom Domain

1. **Vercel**: Add custom domain in Project Settings → Domains
2. **Render**: Add custom domain in Service Settings
3. Update frontend `NEXT_PUBLIC_API_URL` if backend domain changes

---

## Summary

- Push code to GitHub
- Deploy backend: `Render.com` → Connect repo, set Root Dir to `backend`, use `render.yaml`
- Deploy frontend: `Vercel.com` → Connect repo, set Root Dir to `frontend`, set `NEXT_PUBLIC_API_URL` env var
- Frontend calls FastAPI backend via HTTP
- Ready to go!
