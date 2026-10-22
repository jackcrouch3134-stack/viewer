from datetime import datetime
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


def auto_upgrade():
    while True:
        time.sleep(30)
        with lock:
            if backend_ai.modules:
                major, minor, patch = backend_ai.version.split(".")
                backend_ai.version = f"{major}.{minor}.{int(patch) + 1}"
                backend_ai.updates += 1
                state["version"] = backend_ai.version
                state["updates"] = backend_ai.updates


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
    with lock:
        snapshot = build_agent_snapshot()
        backend = snapshot["backend"]
        payload = {
            "system_state": {"status": "online", "autonomous_mode": True},
            "compiled_modules": backend["modules_count"],
            "antenna_version": backend["version"],
            "total_compilations": backend["compilations"],
            "total_updates": backend["updates"],
            "last_activity": datetime.utcnow().isoformat() + "Z",
        }
    payload.update(snapshot)
    return payload


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
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str):
        return jsonify({"error": "code must be a string"}), 400
    with lock:
        result = coordinator.route_compile_request(code)
        state["compilations"] = backend_ai.compilations
        state["version"] = backend_ai.version
        state["modules"][result["module_id"]] = {
            **result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    return jsonify({
        "status": "compiled",
        "module_id": result["module_id"],
        "version": result["version"],
        "optimizations": result["optimizations"],
        "reorganizations": 0,
        "result": result,
        "backend": backend_ai.get_state(),
        "ui": ui_agent.get_state(),
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
    state_result = coordinator.route_gesture(gesture_type, payload)
    return jsonify({
        "status": "ok",
        "state": state_result,
        "ui": ui_agent.get_state(),
    })


@app.route("/api/control", methods=["POST"])
def api_control():
    data = request.get_json(silent=True) or {}
    control = data.get("control")
    value = data.get("value")
    result = coordinator.route_slider_change(control, value)
    return jsonify({
        "status": "ok",
        "result": result,
        "frontend": frontend_ai.get_state(),
    })


@app.route("/api/safety", methods=["POST"])
def api_safety():
    data = request.get_json(silent=True) or {}
    safe_mode = bool(data.get("safe_mode", True))
    strict_mode = bool(data.get("strict_mode", False))
    result = coordinator.route_safety_toggle(safe_mode, strict_mode)
    return jsonify({
        "status": "ok",
        "result": result,
        "frontend": frontend_ai.get_state(),
        "ui": ui_agent.get_state(),
    })


@app.route("/api/alert", methods=["POST"])
def api_alert():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "Alert")
    message = data.get("message", "")
    level = data.get("level", "info")
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
