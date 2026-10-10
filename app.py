from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path

from backend_ai import backend_ai
from frontend_ai import frontend_ai
from ui_agent import ui_agent
from agent_coordinator import AgentCoordinator

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR))

coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/static/<path:name>")
def static_files(name):
    return send_from_directory(STATIC_DIR, name)


@app.route("/api/state")
def api_state():
    return jsonify(coordinator.get_unified_state())


@app.route("/api/compile", methods=["POST"])
def api_compile():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    result = coordinator.route_compile_request(code)
    return jsonify({"status": "ok", "result": result})


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
        "ui": ui_agent.status
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
