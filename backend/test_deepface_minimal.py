import sys
import os
from deepface import DeepFace

img_path = r"data\uploads\9b78cc69-40a0-4cc0-bf06-129bfdb1f873.jpg"
print(f"Testing DeepFace with {img_path}...")
try:
    results = DeepFace.represent(img_path=img_path, model_name="Facenet512", detector_backend="retinaface")
    print(f"Success! Found {len(results)} faces.")
except Exception as e:
    print(f"Error: {e}")
