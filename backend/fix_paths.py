import os
from database import SessionLocal, Media

def fix():
    db = SessionLocal()
    ms = db.query(Media).all()
    count = 0
    missing = 0
    for m in ms:
        if m.file_path.startswith('/app/data/uploads'):
            filename = os.path.basename(m.file_path)
            # Correct local path relative to backend folder
            new_path = f"./data/uploads/{filename}".replace("/", os.sep)
            m.file_path = new_path
            count += 1
            
            # Check if file exists relative to current dir (backend)
            local_full_path = os.path.join('data', 'uploads', filename)
            if not os.path.exists(local_full_path):
                print(f"Warning: File {filename} not found on disk at {os.path.abspath(local_full_path)}")
                missing += 1
    
    db.commit()
    db.close()
    print(f"Updated {count} records. {missing} files are missing on disk.")

if __name__ == "__main__":
    fix()
