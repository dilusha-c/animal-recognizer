FROM python:3.10-slim

WORKDIR /app

# Install build dependencies (45-90 seconds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install (600-900 seconds for TensorFlow)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY models/ ./models/
COPY utils/ ./utils/

EXPOSE 8000

# Increased start-period because TensorFlow initialization takes time
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=2)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
