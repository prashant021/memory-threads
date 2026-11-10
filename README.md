# Memory Threads

**Shared memories, brought together.**

Memory Threads is a privacy-first application for collecting photos and videos from meaningful gatherings and helping guests rediscover the moments they appear in. Guests can optionally scan their face to find matching media, then explore the results in a collage or video reel.

## Features

- Upload event photos and videos
- Optionally search event media using face matching
- Browse matching moments in a collage and video reel
- Process media asynchronously in the background

## Tech stack

- **Frontend:** Next.js, React, Tailwind CSS, Framer Motion
- **Backend:** FastAPI, Python, SQLAlchemy, SQLite
- **Background jobs:** Celery and Redis
- **Face search:** DeepFace with RetinaFace detection, Facenet512 embeddings, and FAISS
- **Media processing:** FFmpeg
- **Deployment:** Docker Compose

## Run locally

### Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- At least 4 GB of memory available to Docker; first startup downloads face-recognition models

### Start the app

```bash
docker compose up --build
```

Then open:

- Frontend: <http://localhost:3000>
- Backend API docs: <http://localhost:8000/docs>

Stop the services with `Ctrl+C`, or run `docker compose down` in another terminal.

## Project layout

```text
backend/    FastAPI application, media and face services, Celery worker
frontend/   Next.js user interface
docker-compose.yml
```

## Privacy

Face scanning is optional. Review the deployment and data-retention settings before using the application with real event media; the operator is responsible for obtaining appropriate consent and protecting uploaded content.

## License

No license has been selected yet. Unless a license is added, default copyright applies and others may not have permission to reuse or distribute this project.
