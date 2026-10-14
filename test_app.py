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


def test_string_jet_engagement_opens_interlock_and_accessalizes_travel():
    client = app.test_client()

    response = client.post("/api/string-jet", json={"engage": True})
    assert response.status_code == 200
    plane = response.get_json()["plane"]
    assert plane["engaged"] is True
    assert plane["interlock_open"] is True
    assert plane["travel_accessalized"] is True

    response = client.post("/api/string-jet", json={"engage": False})
    assert response.status_code == 200
    plane = response.get_json()["plane"]
    assert plane["engaged"] is False
    assert plane["interlock_open"] is False
    assert plane["travel_accessalized"] is False


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
