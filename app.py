import os
from datetime import datetime
import hashlib
import re
import threading
import time
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

from agent_coordinator import AgentCoordinator
from backend_ai import backend_ai
from frontend_ai import frontend_ai
from ui_agent import ui_agent


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR))
server_name = os.getenv("SERVER_NAME") or None
scheme = os.getenv("APP_SCHEME", "https" if _env_bool("APP_HTTPS_ONLY", False) else "http")
app.config.update(
    APP_DOMAIN=os.getenv("APP_DOMAIN", "viewer.local"),
    APP_PORT=int(os.getenv("APP_PORT", "8000")),
    APP_SCHEME=scheme,
    PREFERRED_URL_SCHEME=scheme,
    SERVER_NAME=server_name,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=_env_bool("APP_HTTPS_ONLY", False),
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_NAME="viewer_session",
    MAX_CONTENT_LENGTH=4 * 1024 * 1024,
    SECURITY_HEADERS_ENABLED=True,
)

APP_DOMAIN = app.config["APP_DOMAIN"]
APP_SCHEME = app.config["APP_SCHEME"]
PERSONAL_PROFILE = {
    "observer_name": "JC",
    "project_name": "JC Observer Experience System",
    "identity_name": "JC / Experience Network",
    "mission_title": "Cleaner observation, stronger memory, smarter movement.",
    "mission_summary": "The home screen is framed as a personal experience map: signal quality, learned patterns, and mission awareness stay visible while keeping the JC point of view front and center.",
    "focus_label": "Observer",
    "mode_label": "First Person",
    "footer_line": "JC Observer Experience System v1.0 | Personal signal intelligence",
}


def get_public_base_url():
    domain = APP_DOMAIN
    port = app.config["APP_PORT"]
    if APP_SCHEME == "https" and port == 443:
        return f"{APP_SCHEME}://{domain}"
    if APP_SCHEME == "http" and port == 80:
        return f"{APP_SCHEME}://{domain}"
    return f"{APP_SCHEME}://{domain}:{port}"

state = {
    "compilations": 0,
    "updates": 0,
    "version": "1.0.0",
    "modules": {},
    "settings": {
        "autonomous_mode": True,
        "live_feed": True,
        "safe_mode": True,
        "auto_updates": True,
    },
    "feed": [{
        "id": 1,
        "source": "system",
        "title": "Observation feed active",
        "message": "All sensors are listening for new imagery and telemetry.",
        "level": "info",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }],
    "drawings": [],
}
lock = threading.Lock()
coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)


def push_feed_event(source, title, message, level="info", payload=None):
    """Add a feed event to the live stream state."""
    with lock:
        event = {
            "id": max((item["id"] for item in state["feed"]), default=0) + 1,
            "source": source,
            "title": title,
            "message": message,
            "level": level,
            "payload": payload or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        state["feed"] = [event] + state["feed"][:19]
        return event


def intent_of(code):
    low = code.lower()
    for word, name in (("receive", "receiver"), ("transmit", "transmitter"),
                        ("analyze", "analyzer"), ("process", "processor")):
        if word in low:
            return name
    return "unknown"


def compile_code(code):
    module_id = hashlib.sha256(code.encode()).hexdigest()[:16]
    entry_points = re.findall(r"def\s+(\w+)\s*\(", code)
    with lock:
        state["compilations"] += 1
        state["modules"][module_id] = {
            "module_id": module_id,
            "version": state["version"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "code_intent": intent_of(code),
            "optimizations": len(entry_points),
        }
    return state["modules"][module_id]


def auto_upgrade():
    while True:
        time.sleep(30)
        with lock:
            if state["modules"] and state["settings"]["auto_updates"]:
                major, minor, patch = state["version"].split(".")
                state["version"] = f"{major}.{minor}.{int(patch) + 1}"
                state["updates"] += 1


threading.Thread(target=auto_upgrade, daemon=True).start()


@app.after_request
def add_security_headers(response):
    if app.config.get("SECURITY_HEADERS_ENABLED"):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
    return response


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/static/<path:name>")
def static_assets(name):
    return send_from_directory(STATIC_DIR, name)


@app.route("/icons/<path:filename>")
def icon_assets(filename):
    return send_from_directory(STATIC_DIR / "icons", filename)


@app.route("/<path:filename>")
def root_static_files(filename):
    """Serve static assets at the site root, matching the dashboard HTML."""
    if filename.startswith("api/"):
        abort(404)
    return send_from_directory(STATIC_DIR, filename)


@app.route("/api/state")
@app.route("/api/compiler/state")
def api_state():
    period_days = int(request.args.get("period_days", 7))
    with lock:
        unified = coordinator.get_unified_state(period_days=period_days)
        payload = {
            "system_state": {
                "status": "online",
                "autonomous_mode": state["settings"]["autonomous_mode"],
                "domain": APP_DOMAIN,
                "scheme": APP_SCHEME,
                "observer_name": PERSONAL_PROFILE["observer_name"],
                "project_name": PERSONAL_PROFILE["project_name"],
                "identity_name": PERSONAL_PROFILE["identity_name"],
            },
            "compiled_modules": len(state["modules"]),
            "personal_profile": PERSONAL_PROFILE,
            "motivation_system": unified.get("backend", {}).get("motivation_system", {
                "name": "string motivator",
                "state": {
                    "motivation": "adaptive",
                    "energy": 0.0,
                    "translation": "No signal to convert.",
                    "readability": 0.0,
                    "signal_strength": 0.0,
                },
            }),
            "antenna_version": state["version"],
            "total_compilations": state["compilations"],
            "total_updates": state["updates"],
            "known_numbers": unified["known_numbers"],
            "feed": state["feed"][:5],
            "last_activity": datetime.utcnow().isoformat() + "Z",
            "memory": unified.get("memory", {}),
            "learning": unified.get("learning", {}),
            "last_learned": unified.get("last_learned"),
            "backend": unified.get("backend", {}),
            "frontend": unified.get("frontend", {}),
            "ui": unified.get("ui", {}),
            "period_days": period_days,
            "domain_config": {
                "domain": APP_DOMAIN,
                "scheme": APP_SCHEME,
                "port": app.config["APP_PORT"],
            },
        }
    return jsonify(payload)


@app.route("/api/compile", methods=["POST"])
@app.route("/api/compiler/compile", methods=["POST"])
def api_compile():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    result = coordinator.route_compile_request(code)
    legacy = compile_code(code)
    backend_ai.learning_engine.record_observation(
        context="compile_request",
        outcome=f"compiled:{legacy['module_id']}",
        signal_quality=result.get("signal_quality", 0),
        altitude=result.get("altitude", 0),
        coverage=result.get("coverage", 0),
        confidence=0.82,
        source="compile_api",
    )
    return jsonify({
        "status": "compiled",
        "module_id": legacy["module_id"],
        "version": legacy["version"],
        "optimizations": legacy["optimizations"],
        "reorganizations": 0,
        "result": result,
    })


@app.route("/api/compiler/modules")
def api_modules():
    with lock:
        return jsonify(modules=list(state["modules"].values()))


@app.route("/api/gesture", methods=["POST"])
def api_gesture():
    data = request.get_json(silent=True) or {}
    gesture_type = data.get("type", "drag")
    payload = data.get("data", {})
    state = coordinator.route_gesture(gesture_type, payload)
    return jsonify({"status": "ok", "state": state})


@app.route("/api/control", methods=["POST"])
def api_control():
    data = request.get_json(silent=True) or {}
    control = data.get("control")
    value = data.get("value")
    result = coordinator.route_slider_change(control, value)
    return jsonify({"status": "ok", "result": result})


@app.route("/api/safety", methods=["POST"])
def api_safety():
    data = request.get_json(silent=True) or {}
    safe_mode = bool(data.get("safe_mode", True))
    strict_mode = bool(data.get("strict_mode", False))
    with lock:
        state["settings"]["safe_mode"] = safe_mode
    result = coordinator.route_safety_toggle(safe_mode, strict_mode)
    return jsonify({"status": "ok", "result": result})


@app.route("/api/alert", methods=["POST"])
def api_alert():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "Alert")
    message = data.get("message", "")
    level = data.get("level", "info")
    alert = ui_agent.show_alert(title, message, level)
    return jsonify({"status": "ok", "alert": alert})


@app.route("/api/feedback")
def api_feedback():
    return jsonify(ui_agent.get_pending_feedback())


@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "healthy",
        "backend": backend_ai.status,
        "frontend": frontend_ai.status,
        "ui": ui_agent.status,
    })


@app.route("/api/experience", methods=["GET", "POST"])
def api_experience():
    period_days = int(request.args.get("period_days", 7))
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        context = data.get("context", "manual")
        outcome = data.get("outcome", "observed")
        confidence = float(data.get("confidence", 0.6))
        signal_quality = data.get("signal_quality")
        altitude = data.get("altitude")
        coverage = data.get("coverage")
        source = data.get("source", "user")
        record = backend_ai.learning_engine.record_observation(
            context=context,
            outcome=outcome,
            signal_quality=signal_quality,
            altitude=altitude,
            coverage=coverage,
            confidence=confidence,
            source=source,
        )
        return jsonify({"status": "ok", "record": record, "summary": backend_ai.learning_engine.summarize(period_days=period_days)})

    return jsonify({"experience": backend_ai.learning_engine.summarize(period_days=period_days)})


@app.route("/api/drawings", methods=["GET", "POST"])
def api_drawings():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        drawing = {
            "id": len(state["drawings"]) + 1,
            "title": data.get("title", "Hand-drawn analysis"),
            "source": data.get("source", "upload"),
            "analysis": data.get("analysis", "No analysis provided."),
            "converted_lines": data.get("converted_lines", []),
            "confidence": float(data.get("confidence", 0.6)),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        state["drawings"].append(drawing)
        return jsonify({"status": "ok", "drawing": drawing})
    return jsonify({"drawings": state["drawings"]})


@app.route("/api/feed")
def api_feed():
    with lock:
        return jsonify({"feed": state["feed"]})


@app.route("/api/feed", methods=["POST"])
def api_feed_post():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "system")
    title = data.get("title", "Live feed update")
    message = data.get("message", "New feed event received.")
    level = data.get("level", "info")
    payload = data.get("payload", {})
    event = push_feed_event(source, title, message, level=level, payload=payload)
    return jsonify({"status": "ok", "event": event})


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Settings must be a JSON object"}), 400
        settings = state["settings"]
        updates = {key: value for key, value in data.items() if key in settings}
        if any(type(value) is not bool for value in updates.values()):
            return jsonify({"error": "Settings values must be booleans"}), 400
        with lock:
            settings.update(updates)
    with lock:
        return jsonify({"settings": dict(state["settings"])})


@app.route("/feed")
def live_feed_page():
    return send_from_directory(STATIC_DIR, "feed.html")


@app.route("/settings")
def settings_page():
    return send_from_directory(STATIC_DIR, "settings.html")


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", app.config["APP_PORT"]))
    app.run(host=host, port=port, debug=_env_bool("DEBUG", False), use_reloader=False)
