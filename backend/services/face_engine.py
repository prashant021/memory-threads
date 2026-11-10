import os
import sys
import json
import numpy as np
import faiss
from deepface import DeepFace
import cv2

def _safe_print(msg: str):
    """Print safely on Windows where stdout may be cp1252."""
    try:
        print(msg)
    except UnicodeEncodeError:
        sys.stderr.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        sys.stderr.buffer.flush()

FAISS_INDEX_PATH = "./data/faiss.index"
ID_MAP_PATH = "./data/faiss_id_map.json"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = "retinaface"
EMBEDDING_DIM = 512

class FaceEngine:
    def __init__(self):
        self.index = self._load_index()
        self.id_map = self._load_id_map() # maps faiss index (int) to ExtractedFace.id

    def _load_index(self):
        if os.path.exists(FAISS_INDEX_PATH):
            return faiss.read_index(FAISS_INDEX_PATH)
        return faiss.IndexFlatL2(EMBEDDING_DIM)

    def _load_id_map(self):
        if os.path.exists(ID_MAP_PATH):
            with open(ID_MAP_PATH, "r") as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(ID_MAP_PATH, "w") as f:
            json.dump(self.id_map, f)

    def extract_faces_from_image(self, img_path):
        """
        Extracts face bounding boxes and embeddings from an image.
        Returns a list of dicts: [{'box': [x,y,w,h], 'embedding': [float]}]
        """
        try:
            # Enforce detector to be retinaface, and target model to Facenet512
            results = DeepFace.represent(img_path=img_path, model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND, enforce_detection=True)
            faces = []
            for face in results:
                faces.append({
                    "box": [
                        face["facial_area"]["x"],
                        face["facial_area"]["y"],
                        face["facial_area"]["w"],
                        face["facial_area"]["h"]
                    ],
                    "embedding": face["embedding"]
                })
            return faces
        except ValueError as e:
            # No face detected
            _safe_print(f"ValueError extracting faces from {img_path}: {str(e).encode('ascii', errors='replace').decode('ascii')}")
            return []
        except Exception as e:
            _safe_print(f"Error extracting faces from {img_path}: {str(e).encode('ascii', errors='replace').decode('ascii')}")
            return []

    def save_embeddings(self, media_db, db_session, extracted_faces_data):
        """
        extracted_faces_data: list of dicts from extract_faces_from_image
        """
        from database import ExtractedFace
        
        current_idx = self.index.ntotal
        embeddings = []
        
        for face_data in extracted_faces_data:
            emb = np.array(face_data["embedding"], dtype='float32')
            embeddings.append(emb)
            
            # Save to sqlite
            bbox = face_data["box"]
            db_face = ExtractedFace(
                media_id=media_db.id,
                bbox_x=bbox[0],
                bbox_y=bbox[1],
                bbox_w=bbox[2],
                bbox_h=bbox[3],
                embedding_idx=current_idx
            )
            db_session.add(db_face)
            db_session.flush() # get ID
            
            self.id_map[str(current_idx)] = db_face.id
            current_idx += 1
            
        if embeddings:
            emb_matrix = np.vstack(embeddings)
            self.index.add(emb_matrix)
            self._save_index()
            db_session.commit()

    def search_similar(self, query_img_path, threshold_percent=40.0, max_results=100):
        """
        Search for similarity against stored faces using a percentage-based threshold.
        """
        faces = self.extract_faces_from_image(query_img_path)
        if not faces:
            return []
            
        # For MVP, assume the largest/most prominent face in the query image is the target visitor
        visitor_face = faces[0]
        query_emb = np.array([visitor_face["embedding"]], dtype='float32')
        
        # Facenet512 Euclidean distance mapping to percentage heuristic
        # Distances generally span from 0 (perfect) to ~500 (completely different)
        # We calculate the max acceptable L2 distance based on the percentage
        max_dist = 600.0 * (1.0 - (threshold_percent / 100.0))
        
        distances, indices = self.index.search(query_emb, max_results)
        
        matched_face_ids = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and dist < max_dist:
                face_id = self.id_map.get(str(idx))
                if face_id is not None:
                    matched_face_ids.append(face_id)
                    
        return matched_face_ids

face_engine = FaceEngine()
