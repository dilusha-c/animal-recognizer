# api/predict.py
import sys
import json
import numpy as np
import os
import base64
from io import BytesIO
from PIL import Image

# Suppress TensorFlow warnings and info messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from tensorflow.keras.models import load_model

# Define the path for the temporary model download
TMP_MODEL_PATH = '/tmp/animal_model.h5'
MODEL_URL = 'YOUR_CLOUD_STORAGE_URL'  # Replace with your cloud storage URL

# Function to handle HTTP requests
def handler(request):
    # Get the request body
    try:
        body = json.loads(request.body)
        image_data = body.get('image')
        
        if not image_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data provided'})
            }
        
        # Make prediction
        result = predict_from_base64(image_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'prediction': result})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }

# Function to download model if it doesn't exist
def ensure_model_exists():
    if not os.path.exists(TMP_MODEL_PATH):
        try:
            print("Would download model from cloud storage to temp location")
            
            # For now, we'll look for the model in the project directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(script_dir, '..', 'src')
            model_path = os.path.join(src_dir, 'models', 'animal_model.h5')
            
            if os.path.exists(model_path):
                import shutil
                shutil.copyfile(model_path, TMP_MODEL_PATH)
                print(f"Copied model from {model_path} to {TMP_MODEL_PATH}")
                return True
            else:
                print(f"Model not found at {model_path}")
                return False
        except Exception as e:
            print(f"Error downloading model: {e}")
            return False
    return True

# Load labels
def load_labels():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(script_dir, '..', 'src')
        labels_path = os.path.join(src_dir, 'utils', 'labels.json')
        
        if not os.path.exists(labels_path):
            print(f"Labels file not found at {labels_path}")
            return {}
        
        with open(labels_path) as f:
            labels = json.load(f)
        return {v: k for k, v in labels.items()}
    except Exception as e:
        print(f"Error loading labels: {e}")
        return {}

# Predict from base64 image string
def predict_from_base64(base64_string):
    try:
        # Ensure model is available
        if not ensure_model_exists():
            return "Error: Model not available"
            
        # Load the model
        model = load_model(TMP_MODEL_PATH, compile=False)
        
        # Load labels
        labels = load_labels()
        if not labels:
            return "Error: Labels not available"
            
        # Decode and process the image
        img_data = base64.b64decode(base64_string.split(',')[1] if ',' in base64_string else base64_string)
        img = Image.open(BytesIO(img_data))
        img = img.resize((224, 224))
        
        img_array = np.array(img) / 255.0
        if img_array.shape[2] == 4:  # If RGBA, convert to RGB
            img_array = img_array[:,:,:3]
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        preds = model.predict(img_array, verbose=0)
        class_id = np.argmax(preds[0])
        
        if class_id in labels:
            return labels[class_id]
        else:
            return f"Unknown class ID: {class_id}"
    except Exception as e:
        print(f"Prediction error: {e}")
        return f"Error: {str(e)}"
