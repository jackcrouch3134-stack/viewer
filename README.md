# 🌍 Universal Earth Viewing System

A unified Earth observation and autonomous intelligence platform.

## Features
- satellite observation flow
- atmospheric interpretation
- biological awareness
- autonomous compiler
- direct intelligence translation
- live status dashboard

## Professional web app package

This project is a small Flask-based web app package for the viewer experience.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000

### Health check

```bash
curl http://localhost:8000/health
```

### Docker

```bash
docker build -t viewer-app .
docker run -p 8000:8000 viewer-app
```

### Production-style notes

- App binds to `0.0.0.0` by default
- `HOST` and `PORT` can be overridden via environment variables
- Health endpoint is available at `/health`
