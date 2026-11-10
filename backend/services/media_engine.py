import uuid
import os
from database import SessionLocal, Media
from services.face_engine import face_engine

def process_media(media_id: int):
    # Retrieve media
    db = SessionLocal()
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        db.close()
        return

    try:
        # If it's a video, we would extract frames with ffmpeg.
        # For simplicity in this MVP, if it's a video, we pull a single frame in the middle.
        target_path = media.file_path
        if media.media_type == "video":
            import ffmpeg
            temp_image = f"./data/temp_{media_id}.jpg"
            try:
                (
                    ffmpeg
                    .input(media.file_path, ss=1) # 1 sec in
                    .output(temp_image, vframes=1)
                    .overwrite_output()
                    .run(quiet=True)
                )
                target_path = temp_image
            except Exception as e:
                print(f"Error extracting frame from {media.file_path}: {e}")
                # Fallback, just skip
        
        # Extract faces & add to faiss/db
        faces_data = face_engine.extract_faces_from_image(target_path)
        
        if faces_data:
            face_engine.save_embeddings(media, db, faces_data)
        
        media.status = "indexed"
        
        # cleanup temp image
        if target_path != media.file_path and os.path.exists(target_path):
            os.remove(target_path)
            
    except Exception as e:
        print(f"Failed processing media {media_id}: {e}")
        media.status = "error"
    finally:
        db.commit()
        db.close()

def generate_reel_and_collage(media_paths: list[str], output_dir: str):
    """
    Given matched media files, generates a collage.jpg and a reel.mp4
    """
    import os
    import ffmpeg
    import math
    from PIL import Image

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    collage_path = os.path.abspath(os.path.join(output_dir, "collage.jpg"))
    reel_path = os.path.abspath(os.path.join(output_dir, "reel.mp4"))

    # 1. Generate Collage (just grid of images)
    images = []
    for m in media_paths:
        if m.endswith(('.jpg','.jpeg','.png')):
            images.append(m)
            
    if images:
        try:
            # simple grid
            pil_images = [Image.open(p).convert("RGB").resize((400, 400)) for p in images[:9]]
            grid_size = math.ceil(math.sqrt(len(pil_images)))
            if grid_size > 0:
                collage_width = grid_size * 400
                collage_height = math.ceil(len(pil_images) / grid_size) * 400
                collage = Image.new('RGB', (collage_width, collage_height))
                
                for i, img in enumerate(pil_images):
                    x = (i % grid_size) * 400
                    y = (i // grid_size) * 400
                    collage.paste(img, (x, y))
                    
                collage.save(collage_path)
        except Exception as e:
            print(f"Error generating collage: {e}")

    # 2. Generate Reel
    try:
        import subprocess
        concat_file_path = os.path.abspath(os.path.join(output_dir, "concat.txt"))
        temp_clips = []
        
        # Maximum 10 items for a short ~25 second reel
        for i, m in enumerate(media_paths[:10]):
            ext = m.split('.')[-1].lower()
            clip_path = os.path.join(output_dir, f"clip_{i}.mp4")
            
            try:
                if ext in ['jpg', 'jpeg', 'png']:
                    # Image: 2-second clip with blank audio
                    result = subprocess.run([
                        "ffmpeg", "-y", "-loop", "1", "-i", os.path.abspath(m),
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                        "-c:v", "libx264", "-t", "2",
                        "-pix_fmt", "yuv420p",
                        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30",
                        "-c:a", "aac", "-shortest",
                        os.path.abspath(clip_path)
                    ], capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"FFmpeg clip error: {result.stderr}")
                elif ext in ['mp4', 'mov', 'avi']:
                    # Video: 3-second clip, standardize to 1280x720 30fps with null audio fallback
                    subprocess.run([
                        "ffmpeg", "-y", "-i", m,
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                        "-t", "3",
                        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30",
                        "-pix_fmt", "yuv420p",
                        "-c:v", "libx264", "-c:a", "aac",
                        "-map", "0:v:0", "-map", "1:a:0", # Use video from file, audio from nullsrc to be safe
                        "-shortest",
                        clip_path
                    ], capture_output=True)
                    # ffmpeg `-map 0:a:0?` - if fails it might skip? Actually, to keep it simple, let's just 
                    # standard convert the video to 30fps, 1280x720 and let the concat filter handle it or just hope it has audio.
                    # Wait, simpler: process video with an audio filter that requires audio, but what if no audio?
                    # A robust way without complex maps:
            except Exception as e:
                print(f"Error processing clip {m}: {e}")
                
        # Re-run video clip generation more safely:
        temp_clips = []
        for i, m in enumerate(media_paths[:10]):
            ext = m.split('.')[-1].lower()
            clip_path = os.path.join(output_dir, f"clip_{i}.mp4")
            
            if os.path.exists(clip_path):
                # We used the naive approach above which might fail for videos without audio stream mapping limits.
                pass 
            else:
                if ext in ['mp4', 'mov', 'avi']:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", m,
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                        "-c:v", "libx264", "-t", "3", 
                        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30",
                        "-c:a", "aac", "-shortest",
                        clip_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # basic fallback
            # Only add to temp_clips if the file exists and is not empty (header-only)
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 500:
                temp_clips.append(clip_path)

        if temp_clips:
            with open(concat_file_path, "w") as f:
                for c in temp_clips:
                    fixed_path = c.replace("\\", "/")
                    f.write(f"file '{fixed_path}'\n")
                    
            result = subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", os.path.abspath(concat_file_path),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                os.path.abspath(reel_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg concat error: {result.stderr}")
            
            for c in temp_clips:
                os.remove(c)
            os.remove(concat_file_path)

    except Exception as e:
        print(f"Error generating reel: {e}")

    return {
        "collage": collage_path if os.path.exists(collage_path) else None, 
        "reel": reel_path if os.path.exists(reel_path) else None
    }
