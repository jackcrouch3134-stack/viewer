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
    assert payload["compiled_modules"] == 0

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


def test_external_inputs_are_validated_and_reflected():
    client = app.test_client()

    assert client.post("/api/control", json={"control": "zoom", "value": "x"}).status_code == 400
    assert client.post("/api/control", json={"control": "bogus", "value": 1}).status_code == 400
    assert client.post("/api/safety", json={"safe_mode": "maybe"}).status_code == 400
    assert client.post("/api/compile", json={"code": 5}).status_code == 400
    assert client.post("/api/alert", json={"level": "nope"}).status_code == 400
    assert client.post("/api/gesture", json={"type": 3}).status_code == 400

    response = client.post("/api/control", json={"control": "zoom", "value": 99})
    assert response.status_code == 200
    assert response.get_json()["frontend"]["zoom"] == 3.0

    response = client.post("/api/safety", json={"safe_mode": "false"})
    assert response.get_json()["frontend"]["safe_mode"] is False
    assert response.get_json()["ui"]["safe_mode"] is False
