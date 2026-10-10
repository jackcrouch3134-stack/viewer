import os
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from datetime import datetime
import hashlib
import re
import threading
import time

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR))
app.config["JSON_SORT_KEYS"] = False

state = {
    "compilations": 0,
    "updates": 0,
    "version": "1.0.0",
    "modules": {},
    "autonomy": {
        "challenge_severity": 0.35,
        "safety_bias": 0.8,
        "realism_weight": 0.72,
        "depth_weight": 0.7,
        "last_calibration": "",
    },
}
lock = threading.Lock()


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


def calibrate_challenge(challenge_level=0.35, realism_bias=0.72, depth_bias=0.7, safety_bias=0.8):
    severity = max(0.0, min(1.0, challenge_level))
    realism = max(0.0, min(1.0, realism_bias))
    depth = max(0.0, min(1.0, depth_bias))
    safety = max(0.0, min(1.0, safety_bias))

    moderated_severity = severity * (1.0 - safety * 0.7)
    weighted_realism = realism * 0.85 + (1.0 - moderated_severity) * 0.15
    weighted_depth = depth * 0.9 + moderated_severity * 0.1

    result = {
        "challenge_severity": round(moderated_severity, 3),
        "safety_bias": round(safety, 3),
        "realism_weight": round(weighted_realism, 3),
        "depth_weight": round(weighted_depth, 3),
        "visible_safe": round(1.0 - moderated_severity, 3),
        "perceived_weight": round((weighted_realism + weighted_depth) / 2.0, 3),
        "summary": "Challenge intensity is softened while realism, depth, and weight remain present.",
    }

    with lock:
        state["autonomy"].update(result)
        state["autonomy"]["last_calibration"] = datetime.utcnow().isoformat() + "Z"
    return result


threading.Thread(target=auto_upgrade, daemon=True).start()


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "viewer.html")


@app.route("/<path:name>")
def root_assets(name):
    # lets pages use /style.css, /app.js, /cartoon.html etc.
    return send_from_directory(STATIC_DIR, name)


@app.route("/api/compiler/compile", methods=["POST"])
def api_compile():
    code = (request.get_json(silent=True) or {}).get("code", "")
    m = compile_code(code)
    return jsonify(status="compiled", module_id=m["module_id"], version=m["version"],
                   optimizations=m["optimizations"], reorganizations=0)


@app.route("/api/compiler/modules")
def api_modules():
    with lock:
        return jsonify(modules=list(state["modules"].values()))


@app.route("/api/compiler/state")
def api_state():
    with lock:
        return jsonify(
            system_state={"status": "online", "autonomous_mode": True},
            compiled_modules=len(state["modules"]),
            antenna_version=state["version"],
            total_compilations=state["compilations"],
            total_updates=state["updates"],
            autonomy=state["autonomy"],
            last_activity=datetime.utcnow().isoformat() + "Z",
        )


@app.route("/api/autonomy/calibrate", methods=["POST"])
def api_calibrate():
    payload = request.get_json(silent=True) or {}
    result = calibrate_challenge(
        challenge_level=payload.get("challenge_level", state["autonomy"]["challenge_severity"]),
        realism_bias=payload.get("realism_bias", state["autonomy"]["realism_weight"]),
        depth_bias=payload.get("depth_bias", state["autonomy"]["depth_weight"]),
        safety_bias=payload.get("safety_bias", state["autonomy"]["safety_bias"]),
    )
    return jsonify(result)


@app.route("/health")
def health_check():
    with lock:
        return jsonify({
            "status": "ok",
            "service": "viewer",
            "version": state["version"],
            "modules": len(state["modules"]),
            "autonomous_mode": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })


def run_server():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server()
