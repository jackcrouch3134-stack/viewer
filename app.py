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

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR))

state = {
    "compilations": 0,
    "updates": 0,
    "version": "1.0.0",
    "modules": {},
    "feed": [{
        "id": 1,
        "source": "system",
        "title": "Observation feed active",
        "message": "All sensors are listening for new imagery and telemetry.",
        "level": "info",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }],
}
lock = threading.Lock()
coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)


def push_feed_event(source, title, message, level="info", payload=None):
    """Add a feed event to the live stream state."""
    with lock:
        event = {
            "id": len(state["feed"]) + 1,
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
            if state["modules"]:
                major, minor, patch = state["version"].split(".")
                state["version"] = f"{major}.{minor}.{int(patch) + 1}"
                state["updates"] += 1


threading.Thread(target=auto_upgrade, daemon=True).start()


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/static/<path:name>")
def static_assets(name):
    return send_from_directory(STATIC_DIR, name)


@app.route("/<path:filename>")
def root_static_files(filename):
    """Serve static assets at the site root, matching the dashboard HTML."""
    if filename.startswith("api/"):
        abort(404)
    return send_from_directory(STATIC_DIR, filename)


@app.route("/api/state")
@app.route("/api/compiler/state")
def api_state():
    with lock:
        payload = {
            "system_state": {"status": "online", "autonomous_mode": True},
            "compiled_modules": len(state["modules"]),
            "antenna_version": state["version"],
            "total_compilations": state["compilations"],
            "total_updates": state["updates"],
            "known_numbers": coordinator.get_unified_state()["known_numbers"],
            "feed": state["feed"][:5],
            "last_activity": datetime.utcnow().isoformat() + "Z",
        }
    return jsonify(payload)


@app.route("/api/compile", methods=["POST"])
@app.route("/api/compiler/compile", methods=["POST"])
def api_compile():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    result = coordinator.route_compile_request(code)
    legacy = compile_code(code)
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


@app.route("/feed")
def live_feed_page():
    return send_from_directory(STATIC_DIR, "feed.html")


@app.route("/settings")
def settings_page():
    return send_from_directory(STATIC_DIR, "settings.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
