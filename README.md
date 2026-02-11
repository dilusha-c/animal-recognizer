# Animal Recognizer

Animal Recognizer is a full-stack AI web application that lets users upload an image and instantly identify animals from 64 species using a custom-trained Convolutional Neural Network (CNN) model. It pairs a Next.js (TypeScript) frontend with a FastAPI/TensorFlow backend for fast, reliable, real-time predictions.

**Built June 2025**

**Highlights**
- Real-time animal recognition across 64 species with a Keras CNN model
- Image upload with instant classification routed through Next.js API to Python inference server
- Fast TensorFlow inference served via FastAPI
- Next.js + Tailwind CSS responsive UI
- Google Colab-based training pipeline for the custom CNN

This repo now hosts a **split frontend/backend** setup. The frontend is a Next.js/Tailwind application that runs in Vercel, while the backend is a TensorFlow-powered FastAPI service packaged for Docker and deployed to a Hugging Face Space (containerized backend).

Live demo: https://animal-recognizer.vercel.app/

### Deployments
- Frontend: Vercel at https://animal-recognizer.vercel.app/
- Backend: CI builds and pushes the container image to Docker Hub and retags/pushes to the Hugging Face container registry for the Space.

## Architecture
- `frontend/`: Next.js 15.4.1 + React 19 UI, exposes `/` upload page and `/api/predict` proxy.
- `backend/`: FastAPI 0.104.1 service with `/predict` endpoint, TensorFlow inference, CORS, and Docker support.
- `models/`: Contains `animal_model.h5` and `labels.json` copied into the backend for inference.
- `docker-compose.backend.yml`: Allows spinning up only the backend on EC2 or other hosts.
- CI workflow [`./github/workflows/docker.yml`](./.github/workflows/docker.yml) builds and pushes the backend image to Docker Hub and Hugging Face when backend files or the workflow change.

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
| `NEXT_PUBLIC_API_URL` | Backend URL for the frontend | `http://localhost:8000` (set to your Hugging Face Space URL in production) |

### Proxy Handling
`/api/predict` in the frontend stores uploads temporarily in the OS temp directory, forwards the bytes to FastAPI, and deletes the file immediately.

## Docker & Deployment
### Backend Dockerfile
The backend Dockerfile uses `python:3.10-slim`, installs dependencies, copies the model, and runs `uvicorn main:app` on port `8000`.

### Hugging Face Space (Container)
- CI publishes the image as `registry.huggingface.co/${HF_USERNAME}/animal-recognizer-api:latest`.
- In your Space, choose the Docker image option and set the image to that name; the container listens on port `8000`.
- Secrets required in GitHub Actions: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `HF_USERNAME`, and `HF_TOKEN` to push images.

### CI/CD
GitHub Actions [`.github/workflows/docker.yml`](./.github/workflows/docker.yml) builds/pushes the backend image to Docker Hub and Hugging Face when backend files or the workflow change. Required secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `HF_USERNAME`, `HF_TOKEN`.

## Frontend Deployment (Vercel)
- Set project root to `frontend`
- Build command: `npm run build`
- Environment variable: `NEXT_PUBLIC_API_URL` → Hugging Face Space backend URL (e.g., `https://<your-space>.hf.space`)
- Static `public/` directory exists; no need for `vercel.json`

## Troubleshooting
- **404 on frontend**: Ensure Vercel env var points to the Hugging Face Space backend and the Space is running.
- **Space health check failing**: Confirm the container starts and serves on the expected port (8000 inside the image); review Space logs for startup errors.
- **TensorFlow build heavy**: First Docker build takes 10–15 minutes; use `tensorflow-cpu` in requirements.
- **ESLint/Next.js security warning**: Use Next.js 15.4.1 as in `frontend/package.json`.

## Testing
- Upload an image via the UI; `/api/predict` proxies to the backend and displays the label.
- Check Hugging Face Space logs for backend errors (e.g., TensorFlow load failures).

## Additional Notes
- `frontend/public/.gitkeep` keeps the directory in git for Next.js requirements.
- The backend includes a mock mode if TensorFlow fails; use it during offline development.
- After updates, push to `main` to trigger CI/CD and redeploy.
