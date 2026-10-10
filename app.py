from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path

from backend_ai import backend_ai
from frontend_ai import frontend_ai
from ui_agent import ui_agent
from agent_coordinator import AgentCoordinator
from runtime_state import RuntimeStateStore

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR), template_folder=str(STATIC_DIR))

coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)
runtime_state = RuntimeStateStore()


def api_error(message, status_code=400, details=None):
    payload = {"status": "error", "error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/viewer")
def viewer_page():
    return send_from_directory(STATIC_DIR, "viewer.html")


@app.route("/cartoon")
def cartoon_page():
    return send_from_directory(STATIC_DIR, "cartoon.html")


@app.route("/static/<path:name>")
def static_files(name):
    return send_from_directory(STATIC_DIR, name)


@app.route("/<path:filename>")
def root_static_files(filename):
    """Serve static assets at the site root, matching the dashboard HTML."""
    return send_from_directory(STATIC_DIR, filename)


@app.route("/api/state")
def api_state():
    state = coordinator.get_unified_state()
    state["runtime"] = runtime_state.get_snapshot()
    runtime_state.increment_metric("requests")
    return jsonify(state)


@app.route("/api/compile", methods=["POST"])
def api_compile():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return api_error("Request body must be a JSON object.", 400)

    code = data.get("code", "")
    if not isinstance(code, str):
        return api_error("Code must be a string.", 400)

    try:
        result = coordinator.route_compile_request(code)
    except ValueError:
        return api_error("Invalid compile request.", 400)

    runtime_state.record_event("compile", "Compilation request processed", {"module_id": result.get("module_id")})
    runtime_state.increment_metric("compiles")
    runtime_state.add_alert("Compilation", f"Compiled module {result.get('module_id')}", "success")
    return jsonify({"status": "ok", "result": result, "runtime": runtime_state.get_snapshot()})


@app.route("/api/gesture", methods=["POST"])
def api_gesture():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return api_error("Request body must be a JSON object.", 400)

    gesture_type = data.get("type", "drag")
    payload = data.get("data", {})
    if not isinstance(payload, dict):
        return api_error("Gesture data must be an object.", 400)

    state = coordinator.route_gesture(gesture_type, payload)
    runtime_state.record_event("gesture", f"Gesture processed: {gesture_type}", payload)
    runtime_state.increment_metric("gestures")
    return jsonify({"status": "ok", "state": state, "runtime": runtime_state.get_snapshot()})


@app.route("/api/control", methods=["POST"])
def api_control():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return api_error("Request body must be a JSON object.", 400)

    control = data.get("control")
    value = data.get("value")
    if control is None:
        return api_error("Control name is required.", 400)

    try:
        result = coordinator.route_slider_change(control, value)
    except ValueError:
        return api_error("Unsupported control value.", 400)

    runtime_state.record_event("control", f"Control updated: {control}", {"value": value})
    return jsonify({"status": "ok", "result": result, "runtime": runtime_state.get_snapshot()})


@app.route("/api/safety", methods=["POST"])
def api_safety():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return api_error("Request body must be a JSON object.", 400)

    safe_mode = bool(data.get("safe_mode", True))
    strict_mode = bool(data.get("strict_mode", False))
    result = coordinator.route_safety_toggle(safe_mode, strict_mode)
    runtime_state.record_event("safety", "Safety settings updated", {"safe_mode": safe_mode, "strict_mode": strict_mode})
    return jsonify({"status": "ok", "result": result, "runtime": runtime_state.get_snapshot()})


@app.route("/api/alert", methods=["POST"])
def api_alert():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return api_error("Request body must be a JSON object.", 400)

    title = data.get("title", "Alert")
    message = data.get("message", "")
    level = data.get("level", "info")
    alert = ui_agent.show_alert(title, message, level)
    runtime_state.record_event("alert", title, {"message": message, "level": level})
    runtime_state.add_alert(title, message, level)
    return jsonify({"status": "ok", "alert": alert, "runtime": runtime_state.get_snapshot()})


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
        "runtime": runtime_state.get_snapshot(),
        "system_state": coordinator.get_unified_state()
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
