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

state = {"compilations": 0, "updates": 0, "version": "1.0.0", "modules": {}}
lock = threading.Lock()
coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)


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


def build_agent_snapshot():
    unified = coordinator.get_unified_state()
    backend = unified.get("backend", {})
    frontend = unified.get("frontend", {})
    ui = unified.get("ui", {})
    return {
        "backend": backend,
        "frontend": frontend,
        "ui": ui,
    }


def build_deprecated_state_payload():
    snapshot = build_agent_snapshot()
    with lock:
        compiled_modules = len(state["modules"])
        payload = {
            "system_state": {"status": "online", "autonomous_mode": True},
            "compiled_modules": compiled_modules,
            "antenna_version": state["version"],
            "total_compilations": state["compilations"],
            "total_updates": state["updates"],
            "last_activity": datetime.utcnow().isoformat() + "Z",
        }
    payload.update(snapshot)
    return payload


def error(message, status=400):
    return jsonify({"status": "error", "error": message}), status


def parse_bool(value, default):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    raise ValueError("expected a boolean")


def get_json_object():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


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
    payload = build_deprecated_state_payload()
    return jsonify(payload)


@app.route("/api/compile", methods=["POST"])
@app.route("/api/compiler/compile", methods=["POST"])
def api_compile():
    data = get_json_object()
    code = data.get("code", "")
    if not isinstance(code, str):
        return error("code must be a string")
    result = coordinator.route_compile_request(code)
    legacy = compile_code(code)
    return jsonify({
        "status": "compiled",
        "module_id": legacy["module_id"],
        "version": legacy["version"],
        "optimizations": legacy["optimizations"],
        "reorganizations": 0,
        "result": result,
        **build_agent_snapshot(),
    })


@app.route("/api/compiler/modules")
def api_modules():
    with lock:
        return jsonify(modules=list(state["modules"].values()))


@app.route("/api/gesture", methods=["POST"])
def api_gesture():
    data = get_json_object()
    gesture_type = data.get("type", "drag")
    payload = data.get("data", {})
    if not isinstance(gesture_type, str) or not gesture_type:
        return error("type must be a non-empty string")
    state_result = coordinator.route_gesture(gesture_type, payload)
    return jsonify({
        "status": "ok",
        "state": state_result,
        **build_agent_snapshot(),
    })


@app.route("/api/control", methods=["POST"])
def api_control():
    data = get_json_object()
    control = data.get("control")
    value = data.get("value")
    if control == "zoom":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != value:
            return error("zoom value must be a number")
    elif control == "panel":
        if not isinstance(value, str) or not value:
            return error("panel value must be a non-empty string")
    else:
        return error("unknown control")
    result = coordinator.route_slider_change(control, value)
    return jsonify({
        "status": "ok",
        "result": result,
        **build_agent_snapshot(),
    })


@app.route("/api/safety", methods=["POST"])
def api_safety():
    data = get_json_object()
    try:
        safe_mode = parse_bool(data.get("safe_mode"), True)
        strict_mode = parse_bool(data.get("strict_mode"), False)
    except ValueError:
        return error("safe_mode and strict_mode must be booleans")
    result = coordinator.route_safety_toggle(safe_mode, strict_mode)
    return jsonify({
        "status": "ok",
        "result": result,
        **build_agent_snapshot(),
    })


@app.route("/api/alert", methods=["POST"])
def api_alert():
    data = get_json_object()
    title = data.get("title", "Alert")
    message = data.get("message", "")
    level = data.get("level", "info")
    if not all(isinstance(v, str) for v in (title, message, level)):
        return error("title, message and level must be strings")
    if level not in ("info", "success", "warning", "error"):
        return error("invalid alert level")
    alert = ui_agent.show_alert(title, message, level)
    return jsonify({"status": "ok", "alert": alert, "ui": ui_agent.get_state()})


@app.route("/api/feedback")
def api_feedback():
    return jsonify({**ui_agent.get_pending_feedback(), "ui": ui_agent.get_state()})


@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "healthy",
        "backend": backend_ai.status,
        "frontend": frontend_ai.status,
        "ui": ui_agent.status,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

