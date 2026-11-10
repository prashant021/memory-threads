
import sqlite3
import os

db_path = r"c:\Users\prash\.gemini\antigravity\scratch\memorial-app\backend\data\memorial.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Media Table ---")
    cursor.execute("SELECT id, filename, file_path, status FROM media")
    media = cursor.fetchall()
    for m in media:
        print(f"ID: {m[0]}, Name: {m[1]}, Path: {m[2]}, Status: {m[3]}")
        
    print("\n--- Extracted Faces Table ---")
    cursor.execute("SELECT id, media_id, embedding_idx FROM extracted_faces")
    faces = cursor.fetchall()
    for f in faces:
        print(f"ID: {f[0]}, Media ID: {f[1]}, FAISS Idx: {f[2]}")
        
    print(f"\nTotal Media: {len(media)}")
    print(f"Total Faces: {len(faces)}")
    
    conn.close()
