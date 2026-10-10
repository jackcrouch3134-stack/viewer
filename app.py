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

state = {"compilations": 0, "updates": 0, "version": "1.0.0", "modules": {}}
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


threading.Thread(target=auto_upgrade, daemon=True).start()


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


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
            last_activity=datetime.utcnow().isoformat() + "Z",
        )


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=True)
