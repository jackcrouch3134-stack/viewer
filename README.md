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

## Static asset routing

The dashboard loads CSS and JavaScript from the site root (`/style.css` and `/app.js`). The Flask app serves those files from the `static/` directory while also supporting `/static/...` requests for compatibility.

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

All POST endpoints validate request payloads and return structured error responses when input is missing or invalid.

## Notes

This project is a lightweight prototype designed to illustrate a cooperative agent-based control dashboard. It is intended as a structured foundation for further expansion into more advanced Earth-observation telemetry, autonomous reasoning workflows, or richer front-end dashboards.

## Validation

Use the bundled tests to verify the app remains stable:

```bash
python -m unittest -q
```

## License

This project is provided as a demonstration and can be adapted for educational or experimental use.
