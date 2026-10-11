from app import app


def test_root_assets_are_served_from_static_directory():
    client = app.test_client()

    for path in ["/", "/style.css", "/app.js", "/cartoon.html"]:
        response = client.get(path)
        assert response.status_code == 200, f"{path} should be served successfully"

    static_response = client.get("/static/index.html")
    assert static_response.status_code == 200
    assert b"<html" in static_response.data


def test_api_routes_still_work():
    client = app.test_client()

    response = client.get("/api/compiler/state")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["system_state"]["status"] == "online"
    assert payload["compiled_modules"] == payload["backend"]["modules_count"]
    assert payload["total_compilations"] == payload["backend"]["compilations"]

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "healthy"


def test_dashboard_state_includes_agent_payloads():
    client = app.test_client()

    response = client.get("/api/state")
    assert response.status_code == 200
    payload = response.get_json()
    assert "backend" in payload
    assert "frontend" in payload
    assert "ui" in payload
    assert payload["backend"]["status"] == "ONLINE"
    assert payload["frontend"]["status"] == "ONLINE"
    assert payload["ui"]["status"] == "ONLINE"


def test_agent_actions_keep_unified_and_legacy_state_in_sync():
    client = app.test_client()
    before = client.get("/api/state").get_json()

    compiled = client.post("/api/compile", json={"code": "def receive_data(): pass"})
    assert compiled.status_code == 200
    compile_result = compiled.get_json()
    assert compile_result["module_id"] == compile_result["result"]["module_id"]
    assert compile_result["version"] == compile_result["result"]["version"]

    after_compile = client.get("/api/state").get_json()
    assert after_compile["backend"]["compilations"] == before["backend"]["compilations"] + 1
    assert after_compile["compiled_modules"] == after_compile["backend"]["modules_count"]
    assert after_compile["total_compilations"] == after_compile["backend"]["compilations"]
    assert after_compile["backend"]["modules"][-1]["module_id"] == compile_result["module_id"]

    gesture = client.post("/api/gesture", json={"type": "drag", "data": {"x": 1, "y": 2}})
    assert gesture.get_json()["state"]["count"] == before["ui"]["gesture_history"] + 1

    control = client.post("/api/control", json={"control": "zoom", "value": 2})
    assert control.get_json()["frontend"]["zoom"] == 2

    safety = client.post(
        "/api/safety", json={"safe_mode": False, "strict_mode": True}
    )
    assert safety.get_json()["frontend"]["strict_mode"] is True
    assert safety.get_json()["ui"]["strict_mode"] is True
    assert safety.get_json()["frontend"]["safe_mode"] is False
    assert safety.get_json()["ui"]["safe_mode"] is False

    alert = client.post(
        "/api/alert",
        json={"title": "Test alert", "message": "Test message", "level": "info"},
    )
    assert alert.status_code == 200
    before_feedback = client.get("/api/state").get_json()["ui"]
    assert before_feedback["feedback_count"] == before_feedback["pending_alerts"]

    feedback = client.get("/api/feedback").get_json()
    assert feedback["count"] == before_feedback["feedback_count"]
    after_feedback = client.get("/api/state").get_json()["ui"]
    assert after_feedback["feedback_count"] == 0
    assert after_feedback["pending_alerts"] == 0


def test_compile_rejects_non_string_code():
    response = app.test_client().post("/api/compile", json={"code": []})
    assert response.status_code == 400
