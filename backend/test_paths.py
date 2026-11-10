
import os
OUTPUT_DIR = "./data/outputs"
# Simulate what os.path.join does on Windows
collage_path = os.path.join(OUTPUT_DIR, "94da18e8-35f0-47b9-a255-593cbbd1b42b", "collage.jpg")
print(f"Original Path: {collage_path}")

# This is what main.py does:
replaced = collage_path.replace(OUTPUT_DIR, "")
print(f"Replaced: {replaced}")

# Robust way:
import pathlib
rel = os.path.relpath(collage_path, OUTPUT_DIR)
print(f"Relpath: {rel}")
url = "/api/outputs/" + rel.replace("\\", "/")
print(f"URL: {url}")
