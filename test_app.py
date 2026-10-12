from app import app, push_feed_event, state


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


def test_feed_event_ids_remain_unique_when_feed_is_capped():
    original_feed = state["feed"]
    state["feed"] = [{"id": 1}]
    try:
        ids = [push_feed_event("test", "title", "message")["id"] for _ in range(25)]
        assert len(set(ids)) == len(ids)
        assert ids == list(range(2, 27))
        assert len(state["feed"]) == 20
    finally:
        state["feed"] = original_feed


def test_settings_api_persists_all_boolean_settings():
    client = app.test_client()
    original_settings = state["settings"].copy()
    expected = {
        "autonomous_mode": False,
        "live_feed": False,
        "safe_mode": False,
        "auto_updates": False,
    }
    try:
        response = client.post("/api/settings", json=expected)
        assert response.status_code == 200
        assert response.get_json()["settings"] == expected
        assert client.get("/api/settings").get_json()["settings"] == expected
        assert client.get("/api/state").get_json()["system_state"]["autonomous_mode"] is False
        assert client.post("/api/settings", json={"auto_updates": "false"}).status_code == 400
    finally:
        state["settings"].clear()
        state["settings"].update(original_settings)
