import os
import sys
import shutil
import uuid
from typing import List
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db, Media, ExtractedFace
from sqlalchemy.orm import Session
from services.face_engine import face_engine
from services.media_engine import process_media, generate_reel_and_collage

# Force UTF-8 on Windows to avoid UnicodeEncodeError in cp1252 consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

app = FastAPI(title="Memory Threads API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./data/uploads"
OUTPUT_DIR = "./data/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/api/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/api/upload")
async def upload_media(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    uploaded_records = []
    
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        media_type = "video" if ext in ["mp4", "mov", "avi"] else "image"
        
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.{ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        new_media = Media(filename=file.filename, file_path=file_path, media_type=media_type)
        db.add(new_media)
        db.commit()
        db.refresh(new_media)
        uploaded_records.append(new_media)
        
        # Dispatch background task for face indexing
        background_tasks.add_task(process_media, new_media.id)
        
    return {"message": "Success", "processed": len(uploaded_records)}

@app.get("/api/status")
async def get_status(db: Session = Depends(get_db)):
    total_media = db.query(Media).count()
    indexed_media = db.query(Media).filter(Media.status == "indexed").count()
    error_media = db.query(Media).filter(Media.status == "error").count()
    total_faces = db.query(ExtractedFace).count()
    
    return {
        "media_uploaded": total_media,
        "media_indexed": indexed_media,
        "media_errors": error_media,
        "faces_extracted": total_faces
    }

@app.post("/api/match")
async def match_visitor(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Receives current visitor frame, computes embedding, searches FAISS, finds overlapping media
    """
    print(f"Received match request for file: {file.filename}", flush=True)
    ext = file.filename.split(".")[-1].lower()
    if not ext:
        ext = "jpg"
    visitor_path = os.path.join(UPLOAD_DIR, f"visitor_temp_{uuid.uuid4()}.{ext}")
    
    with open(visitor_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Search against FAISS
        matched_face_ids = face_engine.search_similar(visitor_path, threshold_percent=40.0)
        
        if not matched_face_ids:
            return {"message": "No shared memories found, but we're glad you came to honor them.", "collage": None, "reel": None}
            
        # Get Media IDs where visitor was found
        media_ids = db.query(ExtractedFace.media_id).filter(ExtractedFace.id.in_(matched_face_ids)).distinct().all()
        media_ids = [m[0] for m in media_ids]
        
        if not media_ids:
             return {"message": "No shared media found.", "collage": None, "reel": None}
             
        # Find paths of these media
        intersected_media = db.query(Media).filter(Media.id.in_(media_ids)).all()
        media_paths = [m.file_path for m in intersected_media]
        
        # Generate collage and reel using matched media
        out_dir = os.path.join(OUTPUT_DIR, str(uuid.uuid4()))
        results = generate_reel_and_collage(media_paths, out_dir)
        
        # Generate relative URLs or serve the files
        collage_url = None
        reel_url = None
        
        if results.get("collage"):
            rel_collage = os.path.relpath(results["collage"], OUTPUT_DIR)
            collage_url = "/api/outputs/" + rel_collage.replace("\\", "/")
        if results.get("reel"):
            rel_reel = os.path.relpath(results["reel"], OUTPUT_DIR)
            reel_url = "/api/outputs/" + rel_reel.replace("\\", "/")

        return {
            "message": "Matches found", 
            "collage": collage_url,
            "reel": reel_url,
            "count": len(intersected_media)
        }
    except Exception as e:
        err_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"Error in match_visitor: {err_msg}", flush=True)
        raise HTTPException(status_code=500, detail=f"Face matching failed: {err_msg}")
    finally:
        if os.path.exists(visitor_path):
            os.remove(visitor_path) # don't persist visitor face

