"""
FastAPI backend for Animal Recognizer.
Serves predictions via HTTP endpoint.
"""

import os
import sys
import json
import io
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(title="Animal Recognizer API", version="1.0.0")

# Enable CORS for Vercel frontend
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://*.vercel.app",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load heavy ML libs; fall back to mock predictor if not available
MOCK_MODE = False
model = None
labels = {}

try:
    import numpy as np
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    from tensorflow.keras.models import load_model
except Exception as e:
    print(f"Warning: could not import ML libs: {e}. Using mock predictor.")
    MOCK_MODE = True

# Get the directory of this script (backend folder)
script_dir = Path(__file__).parent.absolute()

# Paths for model and labels (in backend folder)
model_path = script_dir / 'models' / 'animal_model.h5'
labels_path = script_dir / 'utils' / 'labels.json'

# Load model and labels if not in mock mode
if not MOCK_MODE:
    try:
        model = load_model(str(model_path), compile=False)
        with open(labels_path) as f:
            labels = json.load(f)
        labels = {v: k for k, v in labels.items()}
        print(f"Loaded model from {model_path}")
        print(f"Loaded labels from {labels_path}")
    except Exception as e:
        print(f"Warning: failed to load model/labels: {e}. Using mock predictor.")
        MOCK_MODE = True

def predict_animal(image_bytes: bytes) -> str:
    """Predict animal from image bytes."""
    
    # Real prediction with TensorFlow
    if not MOCK_MODE and model is not None:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            preds = model.predict(img_array, verbose=0)
            class_id = int(np.argmax(preds[0]))
            return labels.get(class_id, f"Unknown class ID: {class_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    # Mock predictor for testing (no ML libs)
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Return a mock prediction based on image properties
        return "dog"  # Default mock prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Animal Recognizer API",
        "mode": "mock" if MOCK_MODE else "production"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict animal from uploaded image.
    
    Returns:
        {
            "prediction": "animal_name",
            "confidence": "mock" or float
        }
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read image bytes
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Run prediction
    prediction = predict_animal(image_bytes)
    
    return {
        "prediction": prediction,
        "confidence": "mock" if MOCK_MODE else "unknown"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
