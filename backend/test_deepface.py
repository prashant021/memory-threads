import numpy as np
import cv2
from deepface import DeepFace

# Create a dummy image with a face (just random noise might fail, need a sample or we can just try error handling)
img = np.zeros((400, 400, 3), dtype=np.uint8)
cv2.imwrite("dummy.jpg", img)

try:
    results = DeepFace.represent(img_path="dummy.jpg", model_name="Facenet512", detector_backend="retinaface", enforce_detection=True)
    print("Results:", results)
except Exception as e:
    import traceback
    traceback.print_exc()
