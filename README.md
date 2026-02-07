# Animal Recognizer

This repo now hosts a **split frontend/backed** setup. The frontend is a Next.js/Tailwind application that runs in Vercel, while the backend is a TensorFlow-powered FastAPI service packaged for Docker and deployed on Render (or any container host).

## Architecture
- `frontend/`: Next.js 15.4.1 + React 19 UI, exposes `/` upload page and `/api/predict` proxy.
- `backend/`: FastAPI 0.104.1 service with `/predict` endpoint, TensorFlow inference, CORS, and Docker support.
- `models/`: Contains `animal_model.h5` and `labels.json` copied into the backend for inference.
- `docker-compose.backend.yml`: Allows spinning up only the backend on EC2 or other hosts.
- CI workflow [`./github/workflows/docker.yml`](./.github/workflows/docker.yml) builds and pushes the backend image only when backend files change.

## Getting Started (Local Development)
### Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The FastAPI server loads the TensorFlow model, accepts multipart file uploads, and returns predictions without saving files to disk.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The Next.js app uses `/api/predict` to send images to `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).

### Environment Variables
| Name | Purpose | Default |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Backend URL for the frontend | `http://localhost:8000` |

### Proxy Handling
`/api/predict` in the frontend stores uploads temporarily in the OS temp directory, forwards the bytes to FastAPI, and deletes the file immediately.

## Docker & Deployment
### Backend Dockerfile
The backend Dockerfile uses `python:3.10-slim`, installs dependencies, copies the model, and runs `uvicorn main:app` on port `8000`.

### Render / EC2
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/`
- Use `docker-compose.backend.yml` on EC2 to build/backend:
  ```bash
docker compose -f docker-compose.backend.yml up --build
  ```

### CI/CD
GitHub Actions [`.github/workflows/docker.yml`](./.github/workflows/docker.yml) builds/pushes the backend image to Docker Hub only when backend files or the workflow change. Set `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets to publish images.

## Frontend Deployment (Vercel)
- Set project root to `frontend`
- Build command: `npm run build`
- Environment variable: `NEXT_PUBLIC_API_URL` → Render URL (e.g., `https://animal-recognizer-api.onrender.com`)
- Static `public/` directory exists; no need for `vercel.json`

## Troubleshooting
- **404 on frontend**: Ensure Vercel env var points to backend, and Render backend is running.
- **Render health check failing**: Set health check path to `/` to hit FastAPI root.
- **TensorFlow build heavy**: First Docker build takes 10–15 minutes; use `tensorflow-cpu` in requirements.
- **ESLint/Next.js security warning**: Use Next.js 15.4.1 as in `frontend/package.json`.

## Testing
- Upload an image via the UI; `/api/predict` proxies to the backend and displays the label.
- Backend logs appear in Render, check for errors when TensorFlow cannot load.

## Additional Notes
- `frontend/public/.gitkeep` keeps the directory in git for Next.js requirements.
- The backend includes a mock mode if TensorFlow fails; use it during offline development.
- After updates, push to `main` to trigger CI/CD and redeploy.
