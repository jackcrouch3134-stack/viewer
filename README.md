# 🌍 Universal Earth Viewing System

A unified Earth observation and autonomous intelligence dashboard built around three cooperative AI agents:

- Backend AI: handles compilation, modules, learning, and autonomous upgrades
- Frontend AI: manages visual state, panel selection, zoom, and UI rendering behavior
- UI Agent: tracks clicks, gestures, alerts, notifications, and user interaction feedback

Together they create a real-time Earth-monitoring control center with autonomous systems intelligence.

## Features

- Satellite observation flow
- Atmospheric interpretation
- Biological awareness
- Autonomous compiler
- Direct intelligence translation
- Live status dashboard
- Live observation feed with manually submitted events
- Configurable autonomous, live-feed, safe-mode, and auto-update settings
- Real-time inter-agent state synchronization
- Gesture and interaction monitoring
- Intelligent system status monitoring

## Architecture

This project is organized around a multi-agent design:

- `backend_ai.py` – backend intelligence and compilation engine
- `frontend_ai.py` – front-end state and visual control logic
- `ui_agent.py` – clicks, gestures, alerts, and behavior prediction
- `agent_coordinator.py` – routes actions between the three agents
- `app.py` – Flask API and frontend entry point
- `static/index.html` – dashboard UI
- `static/app.js` – UI logic and live update calls
- `static/style.css` – sci-fi control room styling

## Project Goals

The system is designed to simulate an autonomous Earth viewing and analysis platform where:

- the backend processes and compiles code/modules
- the frontend controls visual state and display behavior
- the user interface agent interprets interaction patterns and feedback
- all three stay synchronized through a central coordinator

## Deployment Domain and Security

The app supports a production-style domain configuration through environment variables. The defaults keep local development simple, but a deployed instance can be configured with a real domain and HTTPS-first policy.

```bash
export APP_DOMAIN=viewer.example.com
export APP_SCHEME=https
export APP_PORT=443
export APP_HTTPS_ONLY=true
export SERVER_NAME=viewer.example.com
export HOST=0.0.0.0
export PORT=443
export DEBUG=false
```

When configured, the app exposes the public base URL through its state payload via `system_state.domain` and `domain_config`, and it adds security headers to serve the app in a more official, locked-frame setup.

## Run

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
python app.py
```

3. Open the app in a browser:

```text
http://localhost:8000
```

For a production deployment, run with the environment variables shown above and serve it behind a TLS terminator or reverse proxy that terminates HTTPS.

## API Endpoints

The app exposes several JSON API routes:

- `GET /api/state` – returns the unified system state
- `POST /api/compile` – triggers the compile pipeline
- `POST /api/gesture` – handles gesture actions
- `POST /api/control` – updates UI controls
- `POST /api/safety` – toggles safe/strict modes
- `POST /api/alert` – creates UI alerts
- `GET /api/feedback` – returns haptic and visual feedback queues
- `GET /api/health` – checks system health
- `GET /api/feed` – returns the latest feed events
- `POST /api/feed` – adds a feed event (`source`, `title`, `message`, `level`, and `payload`)
- `GET /api/settings` – returns the current settings
- `POST /api/settings` – updates boolean settings (`autonomous_mode`, `live_feed`, `safe_mode`, and `auto_updates`)

## Live Feed and Settings

The live observation feed is available at `/feed`; it refreshes from `GET /api/feed` every three seconds and lets users submit events through `POST /api/feed`. The API retains up to 20 recent events in application memory.

The settings page is available at `/settings`. Its settings are held in application memory and can be read or updated through `/api/settings`. Updating `safe_mode` through the settings page also updates the safety API. These values reset when the application restarts.

## Notes

This is a lightweight prototype designed to illustrate a cooperative agent-based control dashboard. It is intended as a structured foundation for further expansion into more advanced Earth-observation telemetry, autonomous reasoning workflows, or richer front-end dashboards.

## License

This project is provided as a demonstration and can be adapted for educational or experimental use.
