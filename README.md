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

This project is a small Flask-based web app package for the viewer experience, with mobile-friendly PWA support.

### Primary master entry

The permanent app entry is `master_app.py`. `app.py` remains a compatibility wrapper that imports the master app so the root viewer experience stays fixed and cannot drift to an alternate dashboard.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# or: python master_app.py
```

Open http://localhost:8000

### Use on a phone browser

- Run the app on the same local network or host it somewhere publicly accessible
- Open the URL in the phone browser
- Use the browser’s “Add to Home Screen” option to install it like an app

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
- Manifest and service worker enable PWA install support on supported browsers
